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
    Skin,
)


def _shift_coordinates(line: Line[int], zoom: int, offset: Coord) -> list[Coord[int]]:
    return [(c + offset) / (zoom + 1) for c in line]


def area_border_text_svg(
    s: AreaBorderText, component: Component, zoom: int, offset: Coord = Coord(0, 0)
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.G()


def area_centre_text_svg(
    s: AreaCentreText, component: Component, zoom: int, offset: Coord = Coord(0, 0)
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    centroid = Line(coordinates).centroid
    return svg.Text(
        x=centroid.x + s.offset.x,
        y=centroid.y + s.offset.y,
        fill=s.colour,
        font_size=s.size,
        text=component.display_name,
        text_anchor="middle",
        stroke="#dddddd",
        stroke_width=0.025 * s.size,
        font_weight="bold",
    )


def area_fill_svg(s: AreaFill, component: Component, zoom: int, offset: Coord = Coord(0, 0)) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.Polygon(
        points=[f"{c.x},{c.y}" for c in coordinates],
        fill=None if s.colour is None else str(s.colour),
        stroke=None if s.outline is None else str(s.outline),
    )


def area_centre_image_svg(
    s: AreaCentreImage, component: Component, zoom: int, offset: Coord = Coord(0, 0)
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.G()


def line_text_svg(s: LineText, component: Component, zoom: int, offset: Coord = Coord(0, 0)) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.G()


def line_back_fore_svg(
    s: LineBack | LineFore, component: Component, zoom: int, offset: Coord = Coord(0, 0)
) -> svg.Element:
    coordinates = _shift_coordinates(component.nodes, zoom, offset)
    return svg.Polyline(
        points=[f"{c.x},{c.y}" for c in coordinates],
        stroke=None if s.colour is None else str(s.colour),
        fill=None,
        fill_opacity=0,
        stroke_width=s.width,
        stroke_dasharray=s.dash,
        stroke_linecap=None if s.unrounded else "round",
        stroke_linejoin="round",
    )


def point_text_svg(s: PointText, component: Component, zoom: int, offset: Coord = Coord(0, 0)) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom, offset)[0]
    return svg.Text(
        x=coordinate.x + s.offset.x,
        y=coordinate.y + s.offset.y,
        fill=s.colour,
        font_size=s.size,
        text=component.display_name,
        text_anchor="middle",
        stroke="#dddddd",
        stroke_width=0.025 * s.size,
        font_weight="bold",
    )


def point_square_svg(s: PointSquare, component: Component, zoom: int, offset: Coord = Coord(0, 0)) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom, offset)[0]
    return svg.G()


def point_image_svg(s: PointImage, component: Component, zoom: int, offset: Coord = Coord(0, 0)) -> svg.Element:
    coordinate = _shift_coordinates(component.nodes, zoom, offset)[0]
    return svg.G()
