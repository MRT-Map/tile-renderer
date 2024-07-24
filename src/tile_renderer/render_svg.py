import functools
from typing import cast

import rich
import svg
from rich.progress import Progress, track
from shapely import Polygon
from shapely.prepared import prep

from tile_renderer.pla2 import Component
from tile_renderer.skin import ComponentStyle, ComponentType, LineBack, LineFore, Skin

type _StylingTuple = tuple[Component, ComponentType, ComponentStyle, int]


def render_svg(components: list[Component], skin: Skin, zoom: int) -> svg.SVG:
    styling = _get_styling(components, skin, zoom)
    styling = _sort_styling(styling, skin)
    text_list = []
    out = svg.SVG(
        elements=[
            a
            for a in (s.render(c, zoom, text_list, skin) for c, ct, s, i in track(styling, "[green]Rendering SVG"))
            if a != svg.G()
        ]
    )
    out.elements.extend(_filter_text_list(text_list))
    return out


def _get_styling(components: list[Component], skin: Skin, zoom: int) -> list[_StylingTuple]:
    out = []
    for component in track(components, "[green]Getting styling"):
        component_type = skin.get_type_by_name(component.type)
        if component_type is None:
            rich.print(
                f"[yellow]Skipping render of {component.type} {component.fid} {f'({component.display_name})' if component.display_name else ''}"
            )
            continue
        styling = component_type.get_styling_by_zoom(zoom)
        if styling is None:
            continue
        for i, style in enumerate(styling):
            out.append((component, component_type, style, i))
    return out


def _sort_styling(styling: list[_StylingTuple], skin: Skin) -> list[_StylingTuple]:
    rich.print("[green]Sorting styling")

    def sort_fn(
        s1: _StylingTuple,
        s2: _StylingTuple,
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


def _filter_text_list(text_list: list[tuple[Polygon, svg.Element]]) -> list[svg.Element]:
    out = []
    with Progress() as progress:
        task_id = progress.add_task("[green]Filtering text", total=len(text_list) ** 2 / 2)
        for i, (shape, text) in enumerate(text_list[::-1]):
            if not any(other.intersects(shape) for other, _ in out):
                out.append((prep(shape), text))
            progress.advance(task_id, i)
        return [text for _, text in out]
