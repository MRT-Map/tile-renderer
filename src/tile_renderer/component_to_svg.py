import uuid
from typing import cast

import svg

from tile_renderer import Component
from tile_renderer.types.coord import Coord, Line
from tile_renderer.types.skin import (
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
)


def _shift_coordinates(line: Line[int], zoom: int, offset: Coord) -> list[Coord[int]]:
    return [(c + offset) / (zoom + 1) for c in line]


def area_border_text_svg(
    s: AreaBorderText,
    component: Component,
    zoom: int,
    text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    if not component.display_name:
        return svg.G()
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    for dash in Line(coordinates).dash(round(0.75 * s.size * len(component.display_name))):
        if dash[0].x > dash[-1].x:
            dash.coords.reverse()
        id_ = str(uuid.uuid4())
        text_list.append(
            (
                dash,
                svg.G(
                    elements=[
                        svg.Polyline(
                            points=[
                                cast(int, f"{c.x},{c.y}") for c in dash.parallel_offset(0.9 * s.size // 2 + s.offset)
                            ],
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
                            font_weight="bold",
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
    text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    centroid = Line(coordinates).point_on_surface
    text_list.append(
        (
            Line(
                [
                    centroid - Coord(0.5 * 0.75 * s.size * len(component.display_name), 0),
                    centroid + Coord(0.5 * 0.75 * s.size * len(component.display_name), 0),
                ]
            ),
            svg.Text(
                x=centroid.x + s.offset.x,
                y=centroid.y + s.offset.y,
                fill=s.colour,
                font_size=s.size,
                text=component.display_name,
                text_anchor="middle",
                stroke="#dddddd",
                stroke_width=0.025 * s.size,
                font_weight="bold",
            ),
        )
    )
    return svg.G()


def area_fill_svg(
    s: AreaFill,
    component: Component,
    zoom: int,
    _text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.Polygon(
        points=[cast(int, f"{c.x},{c.y}") for c in coordinates],
        fill=None if s.colour is None else str(s.colour),
        stroke=None if s.outline is None else str(s.outline),
        stroke_width=s.outline_width,
        stroke_linejoin="round",
    )


def area_centre_image_svg(
    s: AreaCentreImage,
    component: Component,
    zoom: int,
    _text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.G()


def line_text_svg(
    s: LineText, component: Component, zoom: int, text_list: list[tuple[Line, svg.Element]], offset: Coord = Coord(0, 0)
) -> svg.Element:
    if not component.display_name:
        return svg.G()
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    for dash in Line(coordinates).dash(round(0.75 * s.size * len(component.display_name))):
        if dash.shapely.length < 0.9 * 0.75 * s.size * len(component.display_name):
            continue
        if dash[0].x > dash[-1].x:
            dash.coords.reverse()
        id_ = str(uuid.uuid4())
        text_list.append(
            (
                dash,
                svg.G(
                    elements=[
                        svg.Polyline(
                            points=[
                                cast(int, f"{c.x},{c.y}") for c in dash.parallel_offset(0.9 * s.size // 2 + s.offset)
                            ],
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
                            font_weight="bold",
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
    _text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
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
    text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom, offset)[0]
    text_list.append(
        (
            Line(
                [
                    coordinate - Coord(0.5 * 0.75 * s.size * len(component.display_name), 0),
                    coordinate + Coord(0.5 * 0.75 * s.size * len(component.display_name), 0),
                ]
            ),
            svg.Text(
                x=coordinate.x + s.offset.x,
                y=coordinate.y + s.offset.y,
                fill=s.colour,
                font_size=s.size,
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
    _text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom, offset)[0]
    return svg.G()


def point_image_svg(
    s: PointImage,
    component: Component,
    zoom: int,
    _text_list: list[tuple[Line, svg.Element]],
    offset: Coord = Coord(0, 0),
) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom, offset)[0]
    return svg.G()
