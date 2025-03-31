from __future__ import annotations

import base64
import dataclasses
import html
import uuid
from typing import TYPE_CHECKING, cast

import svg
from shapely import Polygon

from tile_renderer.coord import Coord, Line
from tile_renderer.skin import (
    AreaBorderText,
    AreaCentreImage,
    AreaCentreText,
    AreaFill,
    LineBack,
    LineFore,
    LineText,
    PointImage,
    PointSquare,
    PointText,
    Skin,
)

if TYPE_CHECKING:
    from tile_renderer.pla2 import Component


@dataclasses.dataclass
class _Lists:
    @dataclasses.dataclass
    class Text:
        shape: Polygon
        text: svg.Element

    @dataclasses.dataclass
    class Junction:
        i: int
        line: Line[int]
        size: int | float
        fid: str

    text: list[_Lists.Text] = dataclasses.field(default_factory=list)
    junction: list[_Lists.Junction] = dataclasses.field(default_factory=list)
    arrow: list[svg.Polygon] = dataclasses.field(default_factory=list)


def area_border_text_svg(
    s: AreaBorderText,
    component: Component,
    zoom: int,
    skin: Skin,
    lists: _Lists,
    _i: int,
) -> svg.Element:
    if (not component.display_name) or (
        skin.prune_small_text is not None and skin.prune_small_text >= s.size / 2**zoom
    ):
        return svg.G()
    new_coordinates = component.nodes.parallel_offset(s.offset)
    poly = component.nodes.shapely_poly
    if poly is None:
        return svg.G()
    if (s.offset > 0 and not poly.contains(new_coordinates.shapely)) or (
        s.offset < 0 and poly.contains(new_coordinates.shapely)
    ):
        coordinates = component.nodes.parallel_offset(-s.offset)
    else:
        coordinates = new_coordinates
    dashes = coordinates.dash(round(s.size * len(component.display_name))) or []
    for dash in dashes:
        if dash[0].x > dash[-1].x:
            dash.coords.reverse()
        id_ = str(uuid.uuid4())
        lists.text.append(
            _Lists.Text(
                Polygon(
                    a.as_tuple()
                    for a in (dash.parallel_offset(s.size / 2).coords + dash.parallel_offset(-s.size / 2).coords[::-1])
                ),
                svg.G(
                    elements=[
                        svg.Polyline(
                            points=[cast(int, f"{c.x},{c.y}") for c in dash],
                            fill=None,
                            fill_opacity=0,
                            stroke=None,
                            id=id_,
                        ),
                        svg.Text(
                            fill=None if s.colour is None else str(s.colour),
                            font_size=s.size,
                            stroke="#dddddd",
                            stroke_width=0.025 * s.size,
                            font_weight="bolder",
                            dominant_baseline="middle",
                            font_family=skin.font_string,
                            elements=[svg.TextPath(href="#" + id_, text=html.escape(component.display_name))],
                        ),
                    ]
                ),
            )
        )
    return svg.G()


def area_centre_text_svg(
    s: AreaCentreText,
    component: Component,
    _zoom: int,
    skin: Skin,
    lists: _Lists,
    _i: int,
) -> svg.Element:
    centroid = component.nodes.point_on_surface
    lists.text.append(
        _Lists.Text(
            Polygon(
                a.as_tuple()
                for a in (
                    centroid - Coord(0.5 * s.size * len(component.display_name), s.size / 2),
                    centroid - Coord(0.5 * s.size * len(component.display_name), -s.size / 2),
                    centroid + Coord(0.5 * s.size * len(component.display_name), -s.size / 2),
                    centroid + Coord(0.5 * s.size * len(component.display_name), s.size / 2),
                )
            ),
            svg.Text(
                x=centroid.x + s.offset.x,
                y=centroid.y + s.offset.y,
                fill=None if s.colour is None else str(s.colour),
                font_size=s.size,
                font_family=skin.font_string,
                text=html.escape(component.display_name),
                text_anchor="middle",
                stroke="#dddddd",
                stroke_width=0.025 * s.size,
                font_weight="bolder",
            ),
        )
    )
    return svg.G()


def area_fill_svg(
    s: AreaFill,
    component: Component,
    _zoom: int,
    _skin: Skin,
    _lists: _Lists,
    _i: int,
) -> svg.Element:
    return svg.Polygon(
        points=[cast(int, f"{c.x},{c.y}") for c in component.nodes],
        fill=None if s.colour is None else str(s.colour),
        fill_opacity=0 if s.colour is None else None,
        stroke=None if s.outline is None else str(s.outline),
        stroke_width=s.outline_width,
        stroke_linejoin="round",
    )


def area_centre_image_svg(
    s: AreaCentreImage,
    component: Component,
    _zoom: int,
    _skin: Skin,
    _lists: _Lists,
    _i: int,
) -> svg.Element:
    centroid = component.nodes.point_on_surface
    return svg.Image(
        x=centroid.x - s.size.x / 2,
        y=centroid.y - s.size.y / 2,
        width=s.size.x,
        height=s.size.y,
        href=f"data:image/{s.extension};base64,{base64.b64encode(s.image).decode()}",
    )


def line_text_svg(
    s: LineText,
    component: Component,
    zoom: int,
    skin: Skin,
    lists: _Lists,
    _i: int,
) -> svg.Element:
    if "oneWay" in component.tags:
        for dash in (
            component.nodes.parallel_offset(s.offset).dash(
                round(s.size * len(component.display_name or "-" * 8)), shift=True
            )
            or []
        ):
            vector = (dash[-1] - dash[0]).unit()
            pre_arrow_centre = dash.shapely.interpolate(0.5, normalized=True)
            arrow_centre = Coord(pre_arrow_centre.x, pre_arrow_centre.y)
            point1 = arrow_centre + vector * (s.size / 2)
            point2 = arrow_centre - vector * (s.size / 2) + vector.perp() * (s.size / 3)
            point3 = arrow_centre - vector * (s.size / 2) - vector.perp() * (s.size / 3)
            lists.arrow.append(
                svg.Polygon(
                    points=[cast(int, f"{c.x},{c.y}") for c in (point1, point2, point3)],
                    fill=str(s.arrow_colour)
                    if s.arrow_colour is not None
                    else str(s.colour)
                    if s.colour is not None
                    else None,
                    stroke=None,
                )
            )
    if (not component.display_name) or (
        skin.prune_small_text is not None and skin.prune_small_text >= s.size / 2**zoom
    ):
        return svg.G()
    dashes = component.nodes.parallel_offset(s.offset).dash(round(s.size * len(component.display_name))) or []
    for dash in dashes:
        if dash.shapely.length < 0.9 * s.size * len(component.display_name):
            continue
        if dash[0].x > dash[-1].x:
            dash.coords.reverse()
        id_ = str(uuid.uuid4())
        lists.text.append(
            _Lists.Text(
                Polygon(
                    a.as_tuple()
                    for a in (dash.parallel_offset(s.size / 2).coords + dash.parallel_offset(-s.size / 2).coords[::-1])
                ),
                svg.G(
                    elements=[
                        svg.Polyline(
                            points=[cast(int, f"{c.x},{c.y}") for c in dash],
                            fill=None,
                            fill_opacity=0,
                            stroke=None,
                            id=id_,
                        ),
                        svg.Text(
                            fill=str(s.colour),
                            font_size=s.size,
                            stroke="#dddddd",
                            stroke_width=0.025 * s.size,
                            font_family=skin.font_string,
                            font_weight="bolder",
                            dominant_baseline="middle",
                            elements=[svg.TextPath(href="#" + id_, text=html.escape(component.display_name))],
                        ),
                    ]
                ),
            )
        )
    return svg.G()


def line_back_fore_svg(
    s: LineBack | LineFore,
    component: Component,
    _zoom: int,
    _skin: Skin,
    lists: _Lists,
    i: int,
) -> svg.Element:
    if type(s) is LineBack:
        lists.junction.append(_Lists.Junction(i, component.nodes, s.width, component.fid))
    return svg.Polyline(
        points=[cast(int, f"{c.x},{c.y}") for c in component.nodes],
        stroke=None if s.colour is None else str(s.colour),
        fill=None,
        fill_opacity=0,
        stroke_width=s.width,
        stroke_dasharray=s.dash,  # type: ignore[arg-type]
        stroke_linecap=None if s.unrounded else "round",
        stroke_linejoin="round",
    )


def point_text_svg(
    s: PointText,
    component: Component,
    _zoom: int,
    skin: Skin,
    lists: _Lists,
    _i: int,
) -> svg.Element:
    coordinate = component.nodes[0].to_float()
    lists.text.append(
        _Lists.Text(
            Polygon(
                a.as_tuple()
                for a in (
                    coordinate - Coord(0.5 * s.size * len(component.display_name), s.size / 2),
                    coordinate - Coord(0.5 * s.size * len(component.display_name), -s.size / 2),
                    coordinate + Coord(0.5 * s.size * len(component.display_name), -s.size / 2),
                    coordinate + Coord(0.5 * s.size * len(component.display_name), s.size / 2),
                )
            ),
            svg.Text(
                x=coordinate.x + s.offset.x,
                y=coordinate.y + s.offset.y,
                fill=str(s.colour),
                font_size=s.size,
                font_family=skin.font_string,
                text=html.escape(component.display_name),
                text_anchor=s.anchor,
                stroke="#dddddd",
                stroke_width=0.025 * s.size,
                font_weight="bold",
            ),
        )
    )
    return svg.G()


def point_square_svg(
    s: PointSquare,
    component: Component,
    _zoom: int,
    _skin: Skin,
    _lists: _Lists,
    _i: int,
) -> svg.Element:
    coordinate = component.nodes[0]
    return svg.Rect(
        x=coordinate.x - s.size / 2,
        y=coordinate.y - s.size / 2,
        width=s.size,
        height=s.size,
        fill=None if s.colour is None else str(s.colour),
        rx=s.border_radius,
        ry=s.border_radius,
    )


def point_image_svg(
    s: PointImage,
    component: Component,
    _zoom: int,
    _skin: Skin,
    _lists: _Lists,
    _i: int,
) -> svg.Element:
    coordinate = component.nodes[0]
    return svg.Image(
        x=coordinate.x - s.size.x / 2,
        y=coordinate.y - s.size.y / 2,
        width=s.size.x,
        height=s.size.y,
        href=f"data:image/{s.extension};base64,{base64.b64encode(s.image).decode()}",
    )
