import functools
import io
import multiprocessing
import os
import subprocess
from copy import copy
from multiprocessing.managers import BaseManager
from pathlib import Path
from typing import cast

import PIL.Image
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
    print("a")
    return _cut_tile(*args)


def render_tiles(
    components: list[Component],
    skin: Skin,
    zoom: int,
    max_zoom_range: int,
    tile_size: int,
    offset: Coord = Coord(0, 0),
) -> dict[TileCoord, PIL.Image.Image]:
    images = {}
    doc = render_svg(components, skin, zoom, offset)
    tiles = Component.tiles(components, zoom, max_zoom_range)
    img = _export_png(doc, tiles, max_zoom_range * 2**zoom, skin, tile_size)
    with Progress() as progress:
        task_id = progress.add_task("[green] Exporting to PNG", total=len(tiles))
        tile_min_x = min(tiles, key=lambda a: a.x).x
        tile_min_y = min(tiles, key=lambda a: a.y).y

        # for tile, b in pool.imap(_f, ((img, tile, tile_size, tile_min_x, tile_min_y) for tile in tiles)):
        for tile, b in (_cut_tile(img, tile, tile_size, tile_min_x, tile_min_y) for tile in tiles):
            images[tile] = b
            progress.advance(task_id)
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


def _export_png(doc: svg.SVG, tiles: set[TileCoord], zoom_range: int, skin: Skin, tile_size: int) -> PIL.Image.Image:
    x_min = min(tiles, key=lambda a: a.x).bounds(zoom_range).x_min
    y_min = min(tiles, key=lambda a: a.y).bounds(zoom_range).y_min
    x_max = max(tiles, key=lambda a: a.x).bounds(zoom_range).x_max
    y_max = max(tiles, key=lambda a: a.y).bounds(zoom_range).y_max
    doc.viewBox = svg.ViewBoxSpec(
        min_x=x_min,
        min_y=y_min,
        width=x_max - x_min,
        height=y_max - y_min,
    )
    p = subprocess.Popen(
        [
            "resvg",
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--background",
            str(skin.background),
            "--font-family",
            "Noto Sans",
            "--width",
            str(tile_size * (max(tiles, key=lambda a: a.x).x - min(tiles, key=lambda a: a.x).x + 1)),
            "--height",
            str(tile_size * (max(tiles, key=lambda a: a.y).y - min(tiles, key=lambda a: a.y).y + 1)),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return PIL.Image.open(io.BytesIO(p.communicate(input=str(doc).encode("utf-8"))[0]))


def _cut_tile(
    img: PIL.Image.Image,
    tile: TileCoord,
    tile_size: int,
    tile_min_x: int,
    tile_min_y: int,
) -> tuple[TileCoord, PIL.Image.Image]:
    x = (tile.x - tile_min_x) * tile_size
    y = (tile.y - tile_min_y) * tile_size
    return tile, img.crop((x, y, x + tile_size, y + tile_size))


def _export_tile(
    doc: svg.SVG, tile: TileCoord, max_zoom_range: int, skin: Skin, tile_size: int
) -> tuple[TileCoord, bytes]:
    doc2 = copy(doc)
    bounds = tile.bounds(max_zoom_range)
    doc2.viewBox = svg.ViewBoxSpec(
        min_x=bounds.x_min,
        min_y=bounds.y_min,
        width=bounds.x_max - bounds.x_min,
        height=bounds.y_max - bounds.y_min,
    )
    p = subprocess.Popen(
        [
            "resvg",
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--background",
            str(skin.background),
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
    return tile, p.communicate(input=str(doc2).encode("utf-8"))[0]


def _filter_text_list(text_list: list[tuple[Line, svg.Element]]) -> list[svg.Element]:
    out = []
    for line, text in track(text_list, "[green] Filtering text"):
        if not any(line.shapely.intersects(other.shapely) for other, _ in out):
            out.append((line, text))
    return [text for _, text in out]
