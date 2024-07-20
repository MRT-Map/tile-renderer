import functools
import subprocess
from copy import copy
from pathlib import Path

import svg

from tile_renderer.types.coord import TileCoord, Coord
from tile_renderer.types.pla2 import Component
from tile_renderer.types.skin import ComponentStyle, ComponentType, LineBack, LineFore, Skin


def render(
    components: list[Component], skin: Skin, zoom_levels: set[int], max_zoom_range: int, offset: Coord = Coord(0, 0)
) -> dict[TileCoord, bytes]:
    images = {}
    for zoom in zoom_levels:
        styling = _get_styling(components, skin, zoom)
        styling = _sort_styling(styling, skin)
        doc = svg.SVG(elements=[s.render(c, zoom, offset) for c, ct, s, i in styling])
        for tile in Component.tiles(components, zoom, max_zoom_range):
            images[tile] = _export_tile(doc, tile, max_zoom_range, skin)
    return images


def _get_styling(
    components: list[Component], skin: Skin, zoom: int
) -> list[tuple[Component, ComponentType, ComponentStyle, int]]:
    out = []
    for component in components:
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
    def sort_fn(
        s1: tuple[Component, ComponentType, ComponentStyle, int],
        s2: tuple[Component, ComponentType, ComponentStyle, int],
    ) -> float:
        component1, component_type1, style1, i1 = s1
        component2, component_type2, style2, i2 = s2

        if (delta := component1.layer - component2.layer) != 0:
            return delta

        if "road" in component_type1.tags and "road" in component_type2.tags:
            if isinstance(style1, LineBack) and isinstance(style2, LineFore):
                return -1
            if isinstance(style1, LineFore) and isinstance(style2, LineBack):
                return 1

        if (delta := skin.get_order(component_type1.name) - skin.get_order(component_type2.name)) != 0:
            return delta

        return i1 - i2

    return sorted(styling, key=functools.cmp_to_key(sort_fn))


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
