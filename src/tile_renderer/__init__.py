import ctypes
import functools
import multiprocessing
import multiprocessing.sharedctypes
import os
import platform
import re
import subprocess
import tempfile
from pathlib import Path
from typing import cast

import rich
import svg
from rich.progress import Progress, track
from shapely.prepared import prep

from tile_renderer.types.coord import Coord, Line, TileCoord
from tile_renderer.types.pla2 import Component
from tile_renderer.types.skin import ComponentStyle, ComponentType, LineBack, LineFore, Skin


def render_svg(components: list[Component], skin: Skin, zoom: int, offset: Coord = Coord(0, 0)) -> svg.SVG:
    styling = _get_styling(components, skin, zoom)
    styling = _sort_styling(styling, skin)
    text_list = []
    out = svg.SVG(
        elements=[
            a
            for a in (
                s.render(c, zoom, text_list, skin, offset) for c, ct, s, i in track(styling, "[green] Rendering SVG")
            )
            if a != svg.G()
        ]
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
    processes: int = os.cpu_count() * 2,
) -> dict[TileCoord, bytes]:
    images = {}
    doc = render_svg(components, skin, zoom, offset)
    tiles = {t for c in components for t in c.tiles(zoom, max_zoom_range)}

    font_dir = Path(tempfile.gettempdir()) / "tile-renderer" / "fonts"
    font_dir.mkdir(exist_ok=True, parents=True)
    for i, file in enumerate(skin.font_files):
        (font_dir / (str(i) + ".ttf")).write_bytes(file)

    with (
        multiprocessing.Pool(processes=processes) as pool,
        Progress() as progress,
        multiprocessing.Manager() as manager,
    ):
        task_id = progress.add_task("[green] Exporting to PNG", total=len(tiles))
        doc = re.sub(r'<svg width=".*?" height=".*?"', f"<svg viewBox=\"<|min_x|> <|min_y|> {max_zoom_range} {max_zoom_range}\"", _simplify_svg(str(doc), font_dir, tile_size))
        print(doc[:200])
        
        doc = manager.Value(ctypes.c_wchar_p, doc, lock=False)
        resvg_path = subprocess.check_output(["where" if platform.system() == "Windows" else "which", "resvg"]).strip()
        n = 0
        for tile, b in pool.imap(
            _f,
            (
                (
                    doc,
                    tile,
                    max_zoom_range,
                    zoom,
                    offset,
                    str(skin.background),
                    font_dir,
                    tile_size,
                    resvg_path,
                )
                for tile in tiles
            ),
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

def _simplify_svg(doc: str, font_dir: Path, tile_size: int) -> str:
    usvg_path = subprocess.check_output(["where" if platform.system() == "Windows" else "which", "usvg"]).strip()
    p = subprocess.Popen(
        [
            usvg_path,
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--skip-system-fonts",
            "--use-fonts-dir",
            str(font_dir),
            "--default-width",
            str(tile_size),
            "--default-height",
            str(tile_size),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate(input=doc.encode("utf-8"))
    if err:
        print(err)
    return out.decode("utf-8")


def _export_tile(
    doc: multiprocessing.sharedctypes.Synchronized,
    tile: TileCoord,
    max_zoom_range: int,
    zoom: int,
    offset: Coord,
    background: str,
    font_dir: Path,
    tile_size: int,
    resvg_path: str,
) -> tuple[TileCoord, bytes]:
    bounds = tile.bounds(max_zoom_range)
    doc = (
        cast(str, doc.value)
        .replace("<|min_x|>", str((bounds.x_min - offset.x) / 2**zoom), 1)
        .replace("<|min_y|>", str((bounds.y_min - offset.y) / 2**zoom), 1)
    )
    p = subprocess.Popen(
        [
            resvg_path,
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--background",
            background,
            "--skip-system-fonts",
            "--use-fonts-dir",
            str(font_dir),
            "--width",
            str(tile_size),
            "--height",
            str(tile_size),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate(input=doc.encode("utf-8"))
    if err:
        print(err)
    return tile, out


def _filter_text_list(text_list: list[tuple[Line, svg.Element]]) -> list[svg.Element]:
    out = []
    for line, text in track(text_list, "[green] Filtering text"):
        line_sh = line.shapely
        if not any(line_sh.intersects(other) for other, _ in out):
            out.append((line_sh, text))
    return [text for _, text in out]
