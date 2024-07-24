import uuid
from typing import cast

import svg
from shapely import Polygon

from tile_renderer.coord import Coord, Line
from tile_renderer.pla2 import Component
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


def _shift_coordinates(line: Line[int], zoom: int) -> list[Coord[int]]:
    return [c / 2**zoom for c in line]


def area_border_text_svg(
    s: AreaBorderText,
    component: Component,
    zoom: int,
    text_list: list[tuple[Polygon, svg.Element]],
    skin: Skin,
) -> svg.Element:
    if (not component.display_name) or (skin.prune_small_text is not None and skin.prune_small_text >= s.size):
        return svg.G()
    old_coordinates = Line(_shift_coordinates(component.nodes, zoom))
    new_coordinates = old_coordinates.parallel_offset(s.offset)
    poly = Polygon(a.as_tuple() for a in old_coordinates)
    if (s.offset > 0 and not poly.contains(new_coordinates.shapely)) or (
        s.offset < 0 and poly.contains(new_coordinates.shapely)
    ):
        coordinates = old_coordinates.parallel_offset(-s.offset)
    else:
        coordinates = new_coordinates
    dashes = coordinates.dash(round(s.size * len(component.display_name))) or []
    for dash in dashes:
        if dash[0].x > dash[-1].x:
            dash.coords.reverse()
        id_ = str(uuid.uuid4())
        text_list.append(
            (
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
                            fill=s.colour,
                            font_size=s.size,
                            stroke="#dddddd",
                            stroke_width=0.025 * s.size,
                            font_weight="bolder",
                            dominant_baseline="middle",
                            font_family=skin.font_string,
                            elements=[svg.TextPath(href="#" + id_, text=component.display_name)],
                        ),
                    ]
                ),
            )
        )
    return svg.G()


def area_centre_text_svg(
    s: AreaCentreText,
    component: Component,
    zoom: int,
    text_list: list[tuple[Polygon, svg.Element]],
    skin: Skin,
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom)
    centroid = Line(coordinates).point_on_surface
    text_list.append(
        (
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
                fill=s.colour,
                font_size=s.size,
                font_family=skin.font_string,
                text=component.display_name,
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
    zoom: int,
    _text_list: list[tuple[Polygon, svg.Element]],
    _skin: Skin,
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom)
    return svg.Polygon(
        points=[cast(int, f"{c.x},{c.y}") for c in coordinates],
        fill=None if s.colour is None else str(s.colour),
        fill_opacity=0 if s.colour is None else None,
        stroke=None if s.outline is None else str(s.outline),
        stroke_width=s.outline_width,
        stroke_linejoin="round",
    )


def area_centre_image_svg(
    s: AreaCentreImage,
    component: Component,
    zoom: int,
    _text_list: list[tuple[Polygon, svg.Element]],
    _skin: Skin,
) -> svg.Element:
    _shift_coordinates(component.nodes, zoom)
    return svg.G()


def line_text_svg(
    s: LineText,
    component: Component,
    zoom: int,
    text_list: list[tuple[Polygon, svg.Element]],
    skin: Skin,
) -> svg.Element:
    if (not component.display_name) or (skin.prune_small_text is not None and skin.prune_small_text >= s.size):
        return svg.G()
    coordinates = _shift_coordinates(component.nodes, zoom)
    dashes = Line(coordinates).dash(round(s.size * len(component.display_name))) or []
    for dash in dashes:
        if dash.shapely.length < 0.9 * s.size * len(component.display_name):
            continue
        dash.parallel_offset(s.offset)
        if dash[0].x > dash[-1].x:
            dash.coords.reverse()
        id_ = str(uuid.uuid4())
        text_list.append(
            (
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
                            fill=s.colour,
                            font_size=s.size,
                            stroke="#dddddd",
                            stroke_width=0.025 * s.size,
                            font_family=skin.font_string,
                            font_weight="bolder",
                            dominant_baseline="middle",
                            elements=[svg.TextPath(href="#" + id_, text=component.display_name)],
                        ),
                    ]
                ),
            )
        )
    return svg.G()


def line_back_fore_svg(
    s: LineBack | LineFore,
    component: Component,
    zoom: int,
    _text_list: list[tuple[Polygon, svg.Element]],
    _skin: Skin,
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom)
    return svg.Polyline(
        points=[cast(int, f"{c.x},{c.y}") for c in coordinates],
        stroke=None if s.colour is None else str(s.colour),
        fill=None,
        fill_opacity=0,
        stroke_width=s.width,
        stroke_dasharray=s.dash,
        stroke_linecap=None if s.unrounded else "round",
        stroke_linejoin="round",
    )


def point_text_svg(
    s: PointText,
    component: Component,
    zoom: int,
    text_list: list[tuple[Polygon, svg.Element]],
    skin: Skin,
) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom)[0]
    text_list.append(
        (
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
                fill=s.colour,
                font_size=s.size,
                font_family=skin.font_string,
                text=component.display_name,
                text_anchor="middle",
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
    zoom: int,
    _text_list: list[tuple[Polygon, svg.Element]],
    _skin: Skin,
) -> svg.Element:
    _shift_coordinates(component.nodes, zoom)[0]
    return svg.G()


def point_image_svg(
    s: PointImage,
    component: Component,
    zoom: int,
    _text_list: list[tuple[Polygon, svg.Element]],
    _skin: Skin,
) -> svg.Element:
    _shift_coordinates(component.nodes, zoom)[0]
    return svg.G()
