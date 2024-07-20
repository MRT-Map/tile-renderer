import svg

from tile_renderer import Component
from tile_renderer.types.coord import Coord
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


def area_border_text_svg(s: AreaBorderText, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def area_centre_text_svg(s: AreaCentreText, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def area_fill_svg(s: AreaFill, skin: Skin, component: Component, zoom: int) -> svg.Element:
    offset = Coord(0, 0)
    coordinates = [(c + offset) / (zoom + 1) for c in component.nodes]
    return svg.Polygon(
        points=[f"{c.x},{c.y}" for c in coordinates],
        fill=None if s.colour is None else str(s.colour),
        stroke=None if s.outline is None else str(s.outline),
    )


def area_centre_image_svg(s: AreaCentreImage, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def line_text_svg(s: LineText, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def line_back_fore_svg(s: LineBack | LineFore, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def point_text_svg(s: PointText, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def point_square_svg(s: PointSquare, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()


def point_image_svg(s: PointImage, skin: Skin, component: Component, zoom: int) -> svg.Element:
    return svg.G()
