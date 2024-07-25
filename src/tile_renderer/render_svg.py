import dataclasses
import functools
import uuid
from typing import Any, cast

import rich
import svg
from rich.progress import Progress, track
from shapely.prepared import prep

from tile_renderer.component_to_svg import _Lists
from tile_renderer.coord import Coord
from tile_renderer.pla2 import Component
from tile_renderer.skin import ComponentStyle, ComponentType, LineFore, Skin


@dataclasses.dataclass
class _Styling:
    c: Component
    ct: ComponentType
    s: ComponentStyle
    i: int


def render_svg(components: list[Component], skin: Skin, zoom: int) -> svg.SVG:
    styling = _get_styling(components, skin, zoom)
    styling = _sort_styling(styling, skin)
    lists = _Lists()
    out = svg.SVG(
        elements=[
            st.s.render(st.c, zoom, skin, lists, i)
            for i, st in track(enumerate(styling), "[green]Rendering SVG", total=len(styling))
        ]
    )
    for i, elements in _get_junctions(lists.junction, styling):
        for element in elements:
            out.elements.insert(i + 1, element)
    out.elements.extend(_filter_text_list(lists.text))
    out.elements.extend(lists.arrow)
    out.elements = [a for a in out.elements if a != svg.G()]
    return out


def _get_styling(components: list[Component], skin: Skin, zoom: int) -> list[_Styling]:
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
            out.append(_Styling(component, component_type, style, i))
    return out


def _sort_styling(styling: list[_Styling], skin: Skin) -> list[_Styling]:
    rich.print("[green]Sorting styling")

    def sort_fn(
        s1: _Styling,
        s2: _Styling,
    ) -> float:
        if (delta := s1.c.layer - s2.c.layer) != 0:
            return delta

        if (delta := skin.get_order(s1.ct.name) - skin.get_order(s2.ct.name)) != 0:
            return delta

        if s1.c.fid != s2.c.fid:
            return s1.c.fid < s2.c.fid

        return s1.i - s2.i

    return sorted(styling, key=functools.cmp_to_key(cast(Any, sort_fn)))


def _get_junctions(
    junction_list: list[_Lists.Junction],
    styling: list[_Styling],
) -> list[tuple[int, list[svg.Element]]]:
    out: dict[int, list[svg.Element]] = {}
    for jt in track(junction_list, "[green]Calculating road joint junctions"):
        for st in styling[: jt.i]:
            if st.s.__class__ is not LineFore or st.c.fid == jt.fid:
                continue
            s = cast(LineFore, st.s)
            for coord in jt.line:
                id_ = uuid.uuid4()
                mask = svg.Mask(
                    id=str(id_),
                    elements=[
                        svg.Circle(
                            cx=coord.x,
                            cy=coord.y,
                            r=jt.size * 0.75,
                            fill="white",
                        )
                    ],
                )
                for j in (j for j, a in enumerate(st.c.nodes) if a == coord):
                    vector1 = st.c.nodes[j - 1] - coord if j != 0 else None
                    vector2 = st.c.nodes[j + 1] - coord if j != len(st.c.nodes) - 1 else None
                    coord1 = (
                        (coord + vector1.unit() * min(jt.size, abs(vector1)))
                        if vector1 is not None and vector1 != Coord(0, 0)
                        else None
                    )
                    coord2 = (
                        (coord + vector2.unit() * min(jt.size, abs(vector2)))
                        if vector2 is not None and vector2 != Coord(0, 0)
                        else None
                    )
                    coords = [a for a in (coord1, coord, coord2) if a is not None]

                    if mask is not None:
                        out.setdefault(jt.i, []).append(mask)
                        mask = None
                    out.setdefault(jt.i, []).append(
                        svg.Polyline(
                            points=[cast(int, f"{c.x},{c.y}") for c in coords],
                            stroke=None if s.colour is None else str(s.colour),
                            fill=None,
                            fill_opacity=0,
                            stroke_width=s.width,
                            stroke_linecap=None if s.unrounded else "round",
                            stroke_linejoin="round",
                            mask=f"url(#{id_})",
                        )
                    )
    return sorted(out.items(), key=lambda a: -a[0])


def _filter_text_list(text_list: list[_Lists.Text]) -> list[svg.Element]:
    out = []
    with Progress() as progress:
        task_id = progress.add_task("[green]Filtering text", total=len(text_list) ** 2 / 2)
        for i, t in enumerate(text_list[::-1]):
            if not any(other.intersects(t.shape) for other, _ in out):
                out.append((prep(t.shape), t.text))
            progress.advance(task_id, i)
        return [text for _, text in out]
