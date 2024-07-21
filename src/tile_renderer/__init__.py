import functools
import subprocess
from copy import copy
from pathlib import Path
from typing import cast

import rich
import svg
from rich.progress import track

from tile_renderer.types.coord import TileCoord, Coord, Line
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


def render_tiles(
    components: list[Component], skin: Skin, zoom_levels: set[int], max_zoom_range: int, offset: Coord = Coord(0, 0)
) -> dict[TileCoord, bytes]:
    images = {}
    for zoom in zoom_levels:
        doc = render_svg(components, skin, zoom, offset)
        for tile in track(Component.tiles(components, zoom, max_zoom_range), "[green] Exporting to PNG"):
            images[tile] = _export_tile(doc, tile, max_zoom_range, skin)
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


def _export_tile(doc: svg.SVG, tile: TileCoord, max_zoom_range: int, skin: Skin) -> bytes:
    doc2 = copy(doc)
    bounds = tile.bounds(max_zoom_range)
    doc2.viewBox = svg.ViewBoxSpec(
        min_x=bounds.x_min,
        min_y=bounds.y_min,
        width=bounds.x_max - bounds.x_min,
        height=bounds.y_max - bounds.y_min,
    )
    Path("./out.svg").write_text(str(doc2))
    p = subprocess.Popen(
        [
            "resvg",
            "-",
            "/dev/stdout",
            "--resources-dir",
            Path(__file__).parent,
            "--background",
            str(skin.background),
            "--font-family",
            "Noto Sans",
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return p.communicate(input=str(doc2).encode("utf-8"))[0]


def _filter_text_list(text_list: list[tuple[Line, svg.Element]]) -> list[svg.Element]:
    out = []
    for line, text in track(text_list, "[green] Filtering text"):
        if not any(line.shapely.intersects(other.shapely) for other, _ in out):
            out.append((line, text))
    return [text for _, text in out]
