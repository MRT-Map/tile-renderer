import ctypes
import functools
import multiprocessing
import os
import platform
import subprocess
from pathlib import Path
from typing import cast

import rich
import svg
from rich.progress import Progress, track

from tile_renderer.types.coord import Coord, Line, TileCoord
from tile_renderer.types.pla2 import Component
from tile_renderer.types.skin import ComponentStyle, ComponentType, LineBack, LineFore, Skin


def render_svg(components: list[Component], skin: Skin, zoom: int, offset: Coord = Coord(0, 0)) -> svg.SVG:
    styling = _get_styling(components, skin, zoom)
    styling = _sort_styling(styling, skin)
    text_list = []
    out = svg.SVG(
        elements=[s.render(c, zoom, text_list, offset) for c, ct, s, i in track(styling, "[green] Rendering SVG")]
    )
    out.elements.extend(_filter_text_list(text_list))
    return out


def _f(args):
    return _export_tile(*args)


def render_tiles(
    components: list[Component],
    skin: Skin,
    zoom: int,
    max_zoom_range: int,
    tile_size: int,
    offset: Coord = Coord(0, 0),
    processes: int = os.cpu_count(),
) -> dict[TileCoord, bytes]:
    images = {}
    doc = render_svg(components, skin, zoom, offset)
    tiles = Component.tiles(components, zoom, max_zoom_range)
    with (
        multiprocessing.Pool(processes=processes) as pool,
        Progress() as progress,
        multiprocessing.Manager() as manager,
    ):
        task_id = progress.add_task(f"[green] Exporting to PNG", total=len(tiles))
        doc.viewBox = svg.ViewBoxSpec(
            min_x=cast(int, "<|min_x|>"),
            min_y=cast(int, "<|min_y|>"),
            width=tile_size,
            height=tile_size,
        )
        doc = manager.Value(ctypes.c_wchar_p, str(doc))
        resvg_path = subprocess.check_output(["where" if platform.system() == "Windows" else "which", "resvg"]).strip()
        n = 0
        for tile, b in pool.imap(
            _f, ((doc, tile, max_zoom_range, str(skin.background), tile_size, resvg_path) for tile in tiles)
        ):
            images[tile] = b
            progress.advance(task_id)
            n += 1
            if n % 10 == 0:
                progress.console.print(f"{n}/{len(tiles)}")
    return images


def _get_styling(
    components: list[Component], skin: Skin, zoom: int
) -> list[tuple[Component, ComponentType, ComponentStyle, int]]:
    out = []
    for component in track(components, "[green] Getting styling"):
        component_type = skin.get_type_by_name(component.type)
        if component_type is None:
            # TODO log
            continue
        styling = component_type.get_styling_by_zoom(zoom)
        if styling is None:
            continue
        for i, style in enumerate(styling):
            out.append((component, component_type, style, i))
    return out


def _sort_styling(
    styling: list[tuple[Component, ComponentType, ComponentStyle, int]], skin: Skin
) -> list[tuple[Component, ComponentType, ComponentStyle, int]]:
    rich.print("[green] Sorting styling")

    def sort_fn(
        s1: tuple[Component, ComponentType, ComponentStyle, int],
        s2: tuple[Component, ComponentType, ComponentStyle, int],
    ) -> float:
        component1, component_type1, style1, i1 = s1
        component2, component_type2, style2, i2 = s2

        if (delta := component1.layer - component2.layer) != 0:
            return delta

        if "road" in component_type1.tags and "road" in component_type2.tags:
            if style1.__class__ is LineBack and style2.__class__ is LineFore:
                return -1
            if style1.__class__ is LineFore and style2.__class__ is LineBack:
                return 1

        first_road = next(a.name for a in skin.types if "road" in a.tags)
        type_name1 = first_road if "road" in component_type1.tags else component_type1.name
        type_name2 = first_road if "road" in component_type2.tags else component_type2.name

        if (delta := skin.get_order(type_name1) - skin.get_order(type_name2)) != 0:
            return delta

        return i1 - i2

    return sorted(styling, key=functools.cmp_to_key(cast(any, sort_fn)))


def _export_tile(
    doc: str,
    tile: TileCoord,
    max_zoom_range: int,
    background: str,
    tile_size: int,
    resvg_path: str,
) -> tuple[TileCoord, bytes]:
    bounds = tile.bounds(max_zoom_range)
    doc = doc.value.replace("<|min_x|>", str(bounds.x_min)).replace("<|min_y|>", str(bounds.y_min))

    p = subprocess.Popen(
        [
            resvg_path,
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--background",
            background,
            "--font-family",
            "Noto Sans",
            "--width",
            str(tile_size),
            "--height",
            str(tile_size),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return tile, p.communicate(input=doc.encode("utf-8"))[0]


def _filter_text_list(text_list: list[tuple[Line, svg.Element]]) -> list[svg.Element]:
    out = []
    for line, text in track(text_list, "[green] Filtering text"):
        if not any(line.shapely.intersects(other.shapely) for other, _ in out):
            out.append((line, text))
    return [text for _, text in out]
