import functools
import uuid
from typing import Any, cast

import rich
import svg
from rich.progress import Progress, track
from shapely import Polygon
from shapely.prepared import prep

from tile_renderer.coord import Coord, Line
from tile_renderer.pla2 import Component
from tile_renderer.skin import ComponentStyle, ComponentType, LineFore, Skin

type _StylingTuple = tuple[Component, ComponentType, ComponentStyle, int]


def render_svg(components: list[Component], skin: Skin, zoom: int) -> svg.SVG:
    styling = _get_styling(components, skin, zoom)
    styling = _sort_styling(styling, skin)
    text_list = []
    connection_list = []
    out = svg.SVG(
        elements=[
            s.render(c, zoom, skin, text_list, connection_list, i)
            for i, (c, _, s, _) in track(enumerate(styling), "[green]Rendering SVG", total=len(styling))
        ]
    )
    for i, elements in _get_connections(connection_list, styling):
        for element in elements:
            out.elements.insert(i + 1, element)
    out.elements.extend(_filter_text_list(text_list))
    out.elements = [a for a in out.elements if a != svg.G()]
    return out


def _get_styling(components: list[Component], skin: Skin, zoom: int) -> list[_StylingTuple]:
    out = []
    for component in track(components, "[green]Getting styling"):
        component_type = skin.get_type_by_name(component.type)
        if component_type is None:
            rich.print(
                f"[yellow]Skipping render of {component.type} {component.fid} "
                f"{f'({component.display_name})' if component.display_name else ''}"
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

        if (delta := skin.get_order(component_type1.name) - skin.get_order(component_type2.name)) != 0:
            return delta

        if component1.fid != component2.fid:
            return component1.fid < component2.fid

        return i1 - i2

    return sorted(styling, key=functools.cmp_to_key(cast(Any, sort_fn)))


def _get_connections(
    connection_list: list[tuple[int, Line[int], int, str]],
    styling: list[_StylingTuple],
) -> list[tuple[int, list[svg.Element]]]:
    out: dict[int, list[svg.Element]] = {}
    for i, line, size, fid in track(connection_list, "[green]Calculating road joint connections"):
        for c, _, s, _ in styling[:i]:
            if s.__class__ is not LineFore or c.fid == fid:
                continue
            s: LineFore
            for coord in line:
                id_ = uuid.uuid4()
                mask = svg.Mask(
                    id=str(id_),
                    elements=[
                        svg.Circle(
                            cx=coord.x,
                            cy=coord.y,
                            r=size*0.75,
                            fill="white",
                        )
                    ]
                )
                for j in (j for j, a in enumerate(c.nodes) if a == coord):
                    vector1 = c.nodes[j - 1] - coord if j != 0 else None
                    vector2 = c.nodes[j + 1] - coord if j != len(c.nodes) - 1 else None
                    coord1 = (
                        (coord + vector1.unit() * min(size, abs(vector1)))
                        if vector1 is not None and vector1 != Coord(0, 0)
                        else None
                    )
                    coord2 = (
                        (coord + vector2.unit() * min(size, abs(vector2)))
                        if vector2 is not None and vector2 != Coord(0, 0)
                        else None
                    )
                    coords = [a for a in (coord1, coord, coord2) if a is not None]

                    if mask is not None:
                        out.setdefault(i, []).append(mask)
                        mask = None
                    out.setdefault(i, []).append(
                        svg.Polyline(
                            points=[cast(int, f"{c.x},{c.y}") for c in coords],
                            stroke=None if s.colour is None else str(s.colour),
                            fill=None,
                            fill_opacity=0,
                            stroke_width=s.width,
                            stroke_linecap=None if s.unrounded else "round",
                            stroke_linejoin="round",
                            mask=f"url(#{id_})"
                        )
                    )
    return sorted(out.items(), key=lambda a: -a[0])


def _filter_text_list(text_list: list[tuple[Polygon, svg.Element]]) -> list[svg.Element]:
    out = []
    with Progress() as progress:
        task_id = progress.add_task("[green]Filtering text", total=len(text_list) ** 2 / 2)
        for i, (shape, text) in enumerate(text_list[::-1]):
            if not any(other.intersects(shape) for other, _ in out):
                out.append((prep(shape), text))
            progress.advance(task_id, i)
        return [text for _, text in out]
