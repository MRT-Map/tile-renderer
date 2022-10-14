from __future__ import annotations

import functools
import itertools
import math
import re
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import blessed
import imagehash
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from schema import And, Optional, Or, Regex, Schema

import renderer.internals.internal as internal
from renderer import math_utils
from renderer.types import RealNum, SkinJson, SkinType
from renderer.types.coord import ImageCoord, ImageLine, TileCoord
from renderer.types.pla2 import Component

Image.Image.__hash__ = lambda self: int(str(imagehash.average_hash(self)), base=16)


@dataclass(eq=True, unsafe_hash=True)
class _TextObject:
    image: tuple[Image.Image, ...]
    center: tuple[ImageCoord, ...]
    bounds: tuple[tuple[ImageCoord, ...]]

    def __init__(
        self,
        image: Image.Image,
        x: RealNum,
        y: RealNum,
        w: RealNum,
        h: RealNum,
        rot: RealNum,
        tile_coord: TileCoord,
        tile_size: int,
        imd: ImageDraw,
        debug: bool = False,
    ):
        r = functools.partial(
            math_utils.rotate_around_pivot,
            px=tile_coord.x * tile_size + x,
            py=tile_coord.y * tile_size + y,
            theta=-rot,
        )
        self.image = (image,)
        self.center = (
            ImageCoord(tile_coord.x * tile_size + x, tile_coord.y * tile_size + y),
        )
        self.bounds = (
            (
                r(
                    tile_coord.x * tile_size + x - w / 2,
                    tile_coord.y * tile_size + y - h / 2,
                ),
                r(
                    tile_coord.x * tile_size + x - w / 2,
                    tile_coord.y * tile_size + y + h / 2,
                ),
                r(
                    tile_coord.x * tile_size + x + w / 2,
                    tile_coord.y * tile_size + y + h / 2,
                ),
                r(
                    tile_coord.x * tile_size + x + w / 2,
                    tile_coord.y * tile_size + y - h / 2,
                ),
                r(
                    tile_coord.x * tile_size + x - w / 2,
                    tile_coord.y * tile_size + y - h / 2,
                ),
            ),
        )
        if debug:
            nr = functools.partial(
                math_utils.rotate_around_pivot, px=x, py=y, theta=-rot
            )
            imd.line(
                [
                    nr(x - w / 2, y - h / 2),
                    nr(x - w / 2, y + h / 2),
                    nr(x + w / 2, y + h / 2),
                    nr(x + w / 2, y - h / 2),
                    nr(x - w / 2, y - h / 2),
                ],
                fill="#ff0000",
            )

    @classmethod
    def from_multiple(cls, *textobject: _TextObject):
        to = copy(textobject[0])

        to.bounds = tuple(itertools.chain(*[sto.bounds for sto in textobject]))
        to.image = tuple(itertools.chain(*[sto.image for sto in textobject]))
        to.center = tuple(itertools.chain(*[sto.center for sto in textobject]))

        return to


class Skin:
    """Represents a skin.

    :param SkinJson json: The JSON of the skin."""

    def __init__(self, json: SkinJson):
        self.validate_json(json)
        self.tile_size: int = json["info"]["size"]
        self.fonts: dict[str, list[Path]] = {
            name: [Path(path) for path in paths]
            for name, paths in json["info"]["font"].items()
        }
        self.background: str = json["info"]["background"]

        self.order: list[str] = json["order"]
        self.types: dict[str, Skin.ComponentTypeInfo] = {
            name: self.ComponentTypeInfo(name, value, self.order, self)
            for name, value in json["types"].items()
        }

    def __getitem__(self, type_name: str) -> ComponentTypeInfo:
        return self.types[type_name]

    def get_font(
        self, style: str, size: int, assets_dir: Path, rendered_text: str = ""
    ) -> ImageFont.FreeTypeFont:
        """Gets a font, given the style and size.

        :param str style: The style of the font needed, eg. bold, italic etc
        :param int size: The size of the font
        :param Path assets_dir: Where the font is stored
        :param str rendered_text: The text that is rendered with the font, to allow for fallbacks
        :return: The font
        :rtype: ImageFont.FreeTypeFont
        :raises FileNotFoundError: if font is not found"""
        if style in self.fonts.keys():
            for font in self.fonts[style]:
                try:
                    pil_font = ImageFont.truetype(str(assets_dir / font), size)
                except OSError as e:
                    raise FileNotFoundError(
                        f"Could not find font {font} in {assets_dir}"
                    ) from e
                ft_font = TTFont(str(assets_dir / font))
                for table in ft_font["cmap"].tables:
                    if all((ord(char) in table.cmap.keys()) for char in rendered_text):
                        return pil_font
            else:
                return pil_font
        raise FileNotFoundError(f"Font for {style} not found")

    class ComponentTypeInfo:
        """An object representing a component type in the ``types`` portion of a skin.

        :param str name: Will set  ``name``
        :param SkinType json: The JSON of the component type
        :param list[str] order: Will set ``_order``"""

        def __init__(self, name: str, json: SkinType, order: list[str], skin: Skin):
            self.name: str = name
            """The name of the component."""
            self.tags: list[str] = json["tags"]
            """The list of tags attributed to the component."""
            self.shape: Literal["point", "line", "area"] = json["type"]
            """The shape of the component, must be one of ``point``, ``line``, ``area``"""
            self._order = order
            self._skin = skin
            self.styles: dict[
                tuple[int, int], list[Skin.ComponentTypeInfo.ComponentStyle]
            ] = {
                internal._str_to_tuple(range_): [
                    self.ComponentStyle(v, self, shape=self.shape) for v in value
                ]
                for range_, value in json["style"].items()
            }
            """The styles of the object, denoted as ``{(max_zoom, min_zoom): [style, ...]}``"""

        def __getitem__(self, zoom_level: int) -> list[ComponentStyle]:
            for (max_level, min_level), styles in self.styles.items():
                if max_level <= zoom_level <= min_level:
                    return styles
            else:
                return []

        class ComponentStyle:
            # noinspection PyUnresolvedReferences
            """Represents the ``styles`` portion of a ComponentTypeInfo. Base class for all types of ComponentStyle.

            :param dict json: JSON dictionary as input
            :param CompnentTypeInfo type_info: The type_info that the ComponentStyle is under"""

            def __new__(
                cls,
                json: dict | None = None,
                type_info: Skin.ComponentTypeInfo | None = None,
                shape: Literal["point", "line", "area"] | None = None,
            ):
                if cls != Skin.ComponentTypeInfo.ComponentStyle:
                    return super().__new__(cls)
                if shape == "point":
                    if json["layer"] == "circle":
                        return Skin.ComponentTypeInfo.PointCircle.__new__(
                            Skin.ComponentTypeInfo.PointCircle, json, type_info
                        )
                    if json["layer"] == "text":
                        return Skin.ComponentTypeInfo.PointText.__new__(
                            Skin.ComponentTypeInfo.PointText, json, type_info
                        )
                    if json["layer"] == "square":
                        return Skin.ComponentTypeInfo.PointSquare.__new__(
                            Skin.ComponentTypeInfo.PointSquare, json, type_info
                        )
                    if json["layer"] == "image":
                        return Skin.ComponentTypeInfo.PointImage.__new__(
                            Skin.ComponentTypeInfo.PointImage, json, type_info
                        )
                elif shape == "line":
                    if json["layer"] == "text":
                        return Skin.ComponentTypeInfo.LineText.__new__(
                            Skin.ComponentTypeInfo.LineText, json, type_info
                        )
                    if json["layer"] == "back":
                        return Skin.ComponentTypeInfo.LineBack.__new__(
                            Skin.ComponentTypeInfo.LineBack, json, type_info
                        )
                    if json["layer"] == "fore":
                        return Skin.ComponentTypeInfo.LineFore.__new__(
                            Skin.ComponentTypeInfo.LineFore, json, type_info
                        )
                elif shape == "area":
                    if json["layer"] == "bordertext":
                        return Skin.ComponentTypeInfo.AreaBorderText.__new__(
                            Skin.ComponentTypeInfo.AreaBorderText, json, type_info
                        )
                    if json["layer"] == "centertext":
                        return Skin.ComponentTypeInfo.AreaCenterText.__new__(
                            Skin.ComponentTypeInfo.AreaCenterText, json, type_info
                        )
                    if json["layer"] == "fill":
                        return Skin.ComponentTypeInfo.AreaFill.__new__(
                            Skin.ComponentTypeInfo.AreaFill, json, type_info
                        )
                    if json["layer"] == "centerimage":
                        return Skin.ComponentTypeInfo.AreaCenterImage.__new__(
                            Skin.ComponentTypeInfo.AreaCenterImage, json, type_info
                        )
                raise ValueError(f"No layer `{json['layer']}` in shape `{shape}`")

            def render(self, *args, **kwargs):
                """Renders the component into an ImageDraw instance."""

        class PointCircle(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "circle"
                self.colour: str | None = json["colour"]
                self.outline: str | None = json["outline"]
                self.size: int = json["size"]
                self.width: int = json["width"]

            def render(self, imd: ImageDraw.ImageDraw, coords: ImageLine, **_):
                coord = coords.coords[0]
                imd.ellipse(
                    (
                        coord.x - self.size / 2 + 1,
                        coord.y - self.size / 2 + 1,
                        coord.x + self.size / 2,
                        coord.y + self.size / 2,
                    ),
                    fill=self.colour,
                    outline=self.outline,
                    width=self.width,
                )

        class PointText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "text"
                self.colour: str | None = json["colour"]
                self.size: int = json["size"]
                self.offset: ImageCoord = ImageCoord(*json["offset"])
                self.anchor: str = json["anchor"]

            def render(
                self,
                imd: ImageDraw,
                coords: ImageLine,
                display_name: str,
                assets_dir: Path,
                points_text_list: list[_TextObject],
                tile_coord: TileCoord,
                tile_size: int,
                debug: bool = False,
            ):
                coord = coords.coords[0]
                if len(display_name.strip()) == 0:
                    return
                font = self._type_info._skin.get_font(
                    "", self.size + 2, assets_dir, display_name
                )
                text_length = int(imd.textlength(display_name, font))
                pt_i = Image.new(
                    "RGBA", (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0)
                )
                pt_d = ImageDraw.Draw(pt_i)
                pt_d.text(
                    (text_length, self.size + 4),
                    display_name,
                    fill=self.colour,
                    font=font,
                    anchor="mm",
                    stroke_width=1,
                    stroke_fill="#dddddd",
                    spacing=1,
                )
                tw, th = pt_i.size
                pt_i = pt_i.crop((0, 0, pt_i.width, pt_i.height))
                points_text_list.append(
                    _TextObject(
                        pt_i,
                        coord.x + self.offset.x,
                        coord.y + self.offset.y,
                        tw / 2,
                        th / 2,
                        0,
                        tile_coord,
                        tile_size,
                        imd,
                        debug=debug,
                    )
                )

        class PointSquare(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "square"
                self.colour: str | None = json["colour"]
                self.outline: str | None = json["outline"]
                self.size: int = json["size"]
                self.width: int = json["width"]

            def render(self, imd: ImageDraw.ImageDraw, coords: ImageLine, **_):
                coord = coords.coords[0]
                imd.rectangle(
                    (
                        coord.x - self.size / 2 + 1,
                        coord.y - self.size / 2 + 1,
                        coord.x + self.size / 2,
                        coord.y + self.size / 2,
                    ),
                    fill=self.colour,
                    outline=self.outline,
                    width=self.width,
                )

        class PointImage(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "image"
                self.file: Path = Path(json["file"])
                self.offset: ImageCoord = ImageCoord(*json["offset"])

            def render(
                self, img: Image.Image, coords: ImageLine, assets_dir: Path, **_
            ):
                coord = coords.coords[0]
                icon = Image.open(assets_dir / self.file)
                img.paste(
                    icon,
                    (
                        int(coord.x - icon.width / 2 + self.offset.x),
                        int(coord.y - icon.height / 2 + self.offset.y),
                    ),
                    icon,
                )

        class LineText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info: Skin.ComponentTypeInfo = type_info
                self.layer = "text"
                self.arrow_colour: str | None = json["arrow_colour"]
                self.colour: str | None = json["colour"]
                self.size: int = json["size"]
                self.offset: int = json["offset"]

            def _text_on_line(
                self,
                imd: ImageDraw.ImageDraw,
                img: Image.Image,
                font: ImageFont.FreeTypeFont,
                text: str,
                coords: ImageLine,
                tile_coord: TileCoord,
                tile_size: int,
                fill: str | None = None,
                stroke: str | None = None,
                debug: bool = False,
                paste_direct: bool = False,
                upright: bool = True,
            ) -> _TextObject | None:
                char_cursor = 0
                text_to_print = ""
                overflow = 0
                text_objects = []
                swap = coords.coords[-1].x < coords.coords[0].x
                if swap and upright:
                    coords = coords[::-1]
                for c1, c2 in internal._with_next(coords):
                    if c2 == coords[-1]:
                        while char_cursor < len(text):
                            text_to_print += text[char_cursor]
                            char_cursor += 1
                    else:
                        while overflow + imd.textlength(
                            text_to_print, font
                        ) < c1.distance(c2) and char_cursor < len(text):
                            text_to_print += text[char_cursor]
                            char_cursor += 1
                    if char_cursor != len(text):
                        text_to_print = text_to_print[:-1]
                        char_cursor -= 1
                    text_length = int(imd.textlength(text_to_print, font))

                    if text_length != 0:
                        lt_i = Image.new(
                            "RGBA", (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0)
                        )
                        lt_d = ImageDraw.Draw(lt_i)
                        lt_d.text(
                            (text_length, self.size + 4),
                            text_to_print,
                            fill=fill or self.colour,
                            font=font,
                            anchor="mm",
                            stroke_width=1,
                            stroke_fill=stroke or "#dddddd",
                            spacing=1,
                        )
                        tw, th = lt_i.size[:]
                        trot = math.atan2(-c2.y + c1.y, c2.x - c1.x) / math.pi * 180
                        lt_i = lt_i.rotate(trot, expand=True)
                        lt_i = lt_i.crop((0, 0, lt_i.width, lt_i.height))
                        tx = c2.x - (
                            (c2.x - c1.x - overflow * math.cos(trot / 180 * math.pi))
                            / 2
                        )
                        ty = c2.y - (
                            (c2.y - c1.y - overflow * math.sin(trot / 180 * math.pi))
                            / 2
                        )
                        if paste_direct:
                            img.paste(
                                lt_i,
                                (int(tx - lt_i.width / 2), int(ty - lt_i.height / 2)),
                                lt_i,
                            )
                            if debug:
                                nr = functools.partial(
                                    math_utils.rotate_around_pivot,
                                    px=tx,
                                    py=ty,
                                    theta=-trot,
                                )
                                imd.line(
                                    [
                                        nr(tx - tw / 4, ty - th / 4),
                                        nr(tx - tw / 4, ty + th / 4),
                                        nr(tx + tw / 4, ty + th / 4),
                                        nr(tx + tw / 4, ty - th / 4),
                                        nr(tx - tw / 4, ty - th / 4),
                                    ],
                                    fill="#ff0000",
                                )
                        else:
                            text_objects.append(
                                _TextObject(
                                    lt_i,
                                    tx,
                                    ty,
                                    tw / 2,
                                    th / 2,
                                    trot,
                                    tile_coord,
                                    tile_size,
                                    imd,
                                    debug=debug,
                                )
                            )

                    text_to_print = ""
                    overflow = text_length - (c1.distance(c2) - overflow)

                    if char_cursor >= len(text):
                        break
                if text_objects:
                    return _TextObject.from_multiple(*text_objects)
                else:
                    return None

            def render(
                self,
                imd: ImageDraw.ImageDraw,
                img: Image.Image,
                coords: ImageLine,
                assets_dir: Path,
                component: Component,
                text_list: list[_TextObject],
                tile_coord: TileCoord,
                tile_size: int,
                debug: bool = False,
            ):
                if len(component.display_name) == 0:
                    return
                # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Calculating text length")
                font = self._type_info._skin.get_font(
                    "", self.size + 2, assets_dir, component.display_name
                )
                text_length = int(imd.textlength(component.display_name, font))
                if text_length == 0:
                    text_length = int(imd.textlength("----------", font))

                coord_lines = math_utils.dash(
                    coords.parallel_offset(self.offset),
                    text_length,
                    text_length * 1.5,
                )
                if (
                    coord_lines
                    and sum(
                        c1.distance(c2)
                        for c1, c2 in internal._with_next(coord_lines[-1])
                    )
                    < text_length
                ):
                    coord_lines = coord_lines[:-1]
                if debug:
                    imd.line(coords.parallel_offset(self.offset), fill="#ff0000")
                text_list.extend(
                    e
                    for e in (
                        self._text_on_line(
                            imd,
                            img,
                            font,
                            component.display_name,
                            cs,
                            tile_coord,
                            tile_size,
                            debug=debug,
                        )
                        for cs in coord_lines
                    )
                    if e is not None
                )

                if "oneWay" in component.tags:
                    font = self._type_info._skin.get_font(
                        "", self.size + 2, assets_dir, "→"
                    )
                    arrow_coord_lines = math_utils.dash(
                        coords.parallel_offset(self.offset + self.size * 3 / 16),
                        text_length / 2,
                        text_length * 0.75,
                    )
                    if arrow_coord_lines and sum(
                        c1.distance(c2)
                        for c1, c2 in internal._with_next(arrow_coord_lines[-1])
                    ) < int(imd.textlength("→", font)):
                        arrow_coord_lines = arrow_coord_lines[:-1]
                    text_list.extend(
                        e
                        for e in (
                            self._text_on_line(
                                imd,
                                img,
                                font,
                                "→",
                                cs,
                                tile_coord,
                                tile_size,
                                fill=self.arrow_colour,
                                stroke="#00000000",
                                debug=debug,
                                paste_direct=True,
                                upright=False,
                            )
                            for i, cs in enumerate(arrow_coord_lines)
                            if i % 2 != 0
                        )
                        if e is not None
                    )

        class LineBack(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "back"
                self.colour: str | None = json["colour"]
                self.width: int = json["width"]
                self.dash: tuple[int, int] = json["dash"]

            def render(self, imd: ImageDraw.ImageDraw, coords: ImageLine, **_):
                if self.dash is None:
                    imd.line(
                        [(c.x, c.y) for c in coords],
                        fill=self.colour,
                        width=self.width,
                        joint="curve",
                    )
                    if "unroundedEnds" not in self._type_info.tags:
                        imd.ellipse(
                            [
                                coords.coords[0].x - self.width / 2 + 1,
                                coords.coords[0].y - self.width / 2 + 1,
                                coords.coords[0].x + self.width / 2 - 1,
                                coords.coords[0].y + self.width / 2 - 1,
                            ],
                            fill=self.colour,
                        )
                        imd.ellipse(
                            [
                                coords.coords[-1].x - self.width / 2 + 1,
                                coords.coords[-1].y - self.width / 2 + 1,
                                coords.coords[-1].x + self.width / 2 - 1,
                                coords.coords[-1].y + self.width / 2 - 1,
                            ],
                            fill=self.colour,
                        )
                else:
                    for dash_coords in math_utils.dash(
                        coords, self.dash[0], self.dash[1]
                    ):
                        imd.line(dash_coords.coords, fill=self.colour, width=self.width)

        class LineFore(LineBack):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                super().__init__(json, type_info)
                self.layer = "fore"

        class AreaBorderText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "bordertext"
                self.colour: str | None = json["colour"]
                self.offset: int = json["offset"]
                self.size: int = json["size"]

            def render(
                self,
                imd: ImageDraw.ImageDraw,
                coords: ImageLine,
                component: Component,
                assets_dir: Path,
                text_list: list[_TextObject],
                tile_coord: TileCoord,
                tile_size: int,
                debug: bool = False,
            ):
                """TODO fix
                if len(component.display_name.strip()) == 0:
                    return
                font = self._type_info._skin.get_font(
                    "", self.size + 2, assets_dir, component.display_name
                )
                text_length = int(
                    imd.textlength(component.display_name.replace("\n", ""), font)
                )
                for c1, c2 in internal._with_next(coords.coords):
                    if coords.in_bounds(
                        Bounds(
                            x_min=0,
                            x_max=self._type_info._skin.tile_size,
                            y_max=self._type_info._skin.tile_size,
                            y_min=0,
                        )
                    ) and 2 * text_length <= c1.distance(c2):
                        t = math.floor(c1.distance(c2) / (4 * text_length))
                        t = 1 if t == 0 else t
                        all_points: list[
                            list[tuple[ImageCoord, RealNum]]
                        ] = math_utils.midpoint(
                            c1, c2, self.offset, n=t, return_both=True
                        )
                        for n in range(0, len(all_points), 2):
                            p1, p2 = all_points[n][0], all_points[n][1]
                            if self.offset < 0:
                                (tx, ty), trot = (
                                    p1
                                    if not math_utils.point_in_poly(
                                        p1[0].x, p1[0].y, coords
                                    )
                                    else p2
                                )
                            else:
                                (tx, ty), trot = (
                                    p1
                                    if math_utils.point_in_poly(
                                        p1[0].x, p1[0].y, coords
                                    )
                                    else p2
                                )
                            abt_i = Image.new(
                                "RGBA",
                                (2 * text_length, 2 * (self.size + 4)),
                                (0, 0, 0, 0),
                            )
                            abt_d = ImageDraw.Draw(abt_i)
                            abt_d.text(
                                (text_length, self.size + 4),
                                component.display_name.replace("\n", ""),
                                fill=self.colour,
                                font=font,
                                anchor="mm",
                                stroke_width=1,
                                stroke_fill="#dddddd",
                                spacing=1,
                            )
                            tw, th = abt_i.size[:]
                            abt_ir = abt_i.rotate(trot, expand=True)
                            abt_ir = abt_ir.crop((0, 0, abt_ir.width, abt_ir.height))
                            text_list.append(
                                _TextObject(
                                    abt_ir,
                                    tx,
                                    ty,
                                    tw / 2,
                                    th / 2,
                                    trot,
                                    tile_coord,
                                    tile_size,
                                    imd,
                                    debug=debug,
                                )
                            )"""

        class AreaCenterText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "centertext"
                self.colour: str | None = json["colour"]
                self.offset: ImageCoord = ImageCoord(*json["offset"])
                self.size: int = json["size"]

            def render(
                self,
                imd: ImageDraw.ImageDraw,
                coords: ImageLine,
                component: Component,
                assets_dir: Path,
                text_list: list[_TextObject],
                tile_coord: TileCoord,
                tile_size: int,
                debug: bool = False,
            ):
                if len(component.display_name.strip()) == 0:
                    return
                c = coords.centroid
                c.x += self.offset.x
                c.y += self.offset.y
                font = self._type_info._skin.get_font(
                    "", self.size + 2, assets_dir, component.display_name
                )
                text_length = int(
                    min(
                        imd.textlength(x, font)
                        for x in component.display_name.split("\n")
                    )
                )

                left = min(cl.x for cl in coords)
                right = max(cr.x for cr in coords)
                delta = right - left
                if text_length > delta:
                    # logger.log(f"{style.index(self) + 1}/{len(style)} {component.name}: Breaking up string")
                    tokens = component.display_name.split()
                    wss = re.findall(r"\s+", component.display_name)
                    text = ""
                    for token, ws in list(
                        itertools.zip_longest(tokens, wss, fillvalue="")
                    ):
                        temp_text = text[:]
                        temp_text += token
                        if int(imd.textlength(temp_text.split("\n")[-1], font)) > delta:
                            text += "\n" + token + ws
                        else:
                            text += token + ws
                    text_length = int(
                        max(imd.textlength(x, font) for x in text.split("\n"))
                    )
                    text_size = int(imd.textsize(text, font)[1] + 4)
                else:
                    text = component.display_name
                    text_size = self.size + 4

                act_i = Image.new(
                    "RGBA", (2 * text_length, 2 * text_size), (0, 0, 0, 0)
                )
                act_d = ImageDraw.Draw(act_i)
                act_d.multiline_text(
                    (text_length, text_size),
                    text,
                    fill=self.colour,
                    font=font,
                    anchor="mm",
                    stroke_width=1,
                    stroke_fill="#dddddd",
                    align="center",
                )
                cw, ch = act_i.size[:]
                act_i = act_i.crop((0, 0, act_i.width, act_i.height))
                text_list.append(
                    _TextObject(
                        act_i,
                        c.x,
                        c.y,
                        cw / 2,
                        ch / 2,
                        0,
                        tile_coord,
                        tile_size,
                        imd,
                        debug=debug,
                    )
                )

        class AreaFill(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "fill"
                self.colour: str | None = json["colour"]
                self.outline: str | None = json["outline"]
                self.stripe: tuple[int, int, int] | None = (
                    None if json["stripe"] is None else tuple(json["stripe"])
                )

            def render(
                self,
                imd: ImageDraw.ImageDraw,
                img: Image.Image,
                coords: ImageLine,
                component: Component,
                tile_coord: TileCoord,
                size: int,
                **_,
            ):
                ai = Image.new(
                    "RGBA",
                    (self._type_info._skin.tile_size, self._type_info._skin.tile_size),
                    (0, 0, 0, 0),
                )
                ad = ImageDraw.Draw(ai)

                if self.stripe is not None:
                    # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Generating stripes")
                    bounds = coords.bounds
                    bounds.x_max += bounds.x_max - bounds.x_min
                    bounds.x_min -= bounds.y_max - bounds.y_min
                    bounds.y_max += bounds.x_max - bounds.x_min
                    bounds.y_min -= bounds.y_max - bounds.y_min
                    af_i = Image.new(
                        "RGBA",
                        (
                            self._type_info._skin.tile_size,
                            self._type_info._skin.tile_size,
                        ),
                        (0, 0, 0, 0),
                    )
                    af_d = ImageDraw.Draw(af_i)
                    tlx = bounds.x_min - 1
                    while tlx <= bounds.x_max:
                        af_d.polygon(
                            [
                                (tlx, bounds.y_min),
                                (tlx + self.stripe[0], bounds.y_min),
                                (tlx + self.stripe[0], bounds.y_max),
                                (tlx, bounds.y_max),
                            ],
                            fill=self.colour,
                        )
                        tlx += self.stripe[0] + self.stripe[1]
                    af_i = af_i.rotate(self.stripe[2], center=coords.centroid)
                    mi = Image.new(
                        "RGBA",
                        (
                            self._type_info._skin.tile_size,
                            self._type_info._skin.tile_size,
                        ),
                        (0, 0, 0, 0),
                    )
                    md = ImageDraw.Draw(mi)
                    md.polygon(coords.coords, fill=self.colour)
                    pi = Image.new(
                        "RGBA",
                        (
                            self._type_info._skin.tile_size,
                            self._type_info._skin.tile_size,
                        ),
                        (0, 0, 0, 0),
                    )
                    pi.paste(af_i, (0, 0), mi)
                    ai.paste(pi, (0, 0), pi)
                else:
                    # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Filling area")
                    ad.polygon(coords.coords, fill=self.colour, outline=self.outline)

                """if component.hollows is not None:
                    for n in component.hollows:
                        n_coords = _node_list_to_image_coords(
                            n, nodes, self._type_info._skin, tile_coord, size
                        )
                        ad.polygon(n_coords, fill=(0, 0, 0, 0))       """
                img.paste(ai, (0, 0), ai)

                if self.outline is not None:
                    # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Drawing outline")
                    exterior_outline = coords[:]
                    exterior_outline.append(exterior_outline[0])
                    outlines = [exterior_outline]
                    """if component.hollows is not None:
                        for n in component.hollows:
                            n_coords = _node_list_to_image_coords(
                                n, nodes, self._type_info._skin, tile_coord, size
                            )
                            n_coords.append(n_coords[0])
                            outlines.append(n_coords)  """
                    for o_coords in outlines:
                        imd.line(o_coords, fill=self.outline, width=2, joint="curve")

        class AreaCenterImage(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self.type_info: Skin.ComponentTypeInfo = type_info
                self.layer = "centerimage"
                self.file: Path = Path(json["file"])
                self.offset: ImageCoord = ImageCoord(*json["offset"])

            def render(
                self, img: Image.Image, coords: ImageLine, assets_dir: Path, **_
            ):
                cx, cy = coords.centroid
                icon = Image.open(assets_dir / self.file)
                img.paste(icon, (cx + self.offset.x, cy + self.offset.y), icon)

    @classmethod
    def from_name(cls, name: str = "default") -> Skin:
        """
        Gets a skin from inside the package.

        :param str name: the name of the skin

        :returns: The skin
        :rtype: Skin

        :raises FileNotFoundError: if skin does not exist
        """
        try:
            return cls(
                internal._read_json(
                    Path(__file__).parent.parent / "skins" / (name + ".json")
                )
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Skin '{name}' not found")

    @staticmethod
    def validate_json(json: dict) -> Literal[True]:
        """
        Validates a skin JSON file.

        :param SkinJson json: the skin JSON file

        :returns: Returns True if no errors
        """
        main_schema = Schema(
            {
                "info": {
                    "size": int,
                    "font": {"": [str], "b": [str], "i": [str], "bi": [str]},
                    "background": And(str, Regex(r"^#[a-f,0-9]{3,6}$")),
                },
                "order": [str],
                "types": {
                    str: {
                        "tags": list,
                        "type": lambda t_: t_ in ["point", "line", "area"],
                        "style": {Optional(str): list},
                    }
                },
            }
        )
        point_circle = Schema(
            {
                "layer": "circle",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "outline": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "size": int,
                "width": int,
            }
        )
        point_text = Schema(
            {
                "layer": "text",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "offset": And([int], lambda o: len(o) == 2),
                "size": int,
                "anchor": Or(None, str),
            }
        )
        point_square = Schema(
            {
                "layer": "square",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "outline": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "size": int,
                "width": int,
            }
        )
        point_image = Schema(
            {"layer": "image", "file": str, "offset": And([int], lambda o: len(o) == 2)}
        )
        line_backfore = Schema(
            {
                "layer": Or("back", "fore"),
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "width": int,
                Optional("dash"): Or(None, And([int], lambda l: len(l) == 2)),
            }
        )
        line_text = Schema(
            {
                "layer": "text",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "arrow_colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "size": int,
                "offset": int,
            }
        )
        area_fill = Schema(
            {
                "layer": "fill",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "outline": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                Optional("stripe"): Or(None, And([int], lambda l: len(l) == 3)),
            }
        )
        area_bordertext = Schema(
            {
                "layer": "bordertext",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "offset": int,
                "size": int,
            }
        )
        area_centertext = Schema(
            {
                "layer": "centertext",
                "colour": Or(None, And(str, Regex(r"^#[a-f,0-9]{3,6}$"))),
                "size": int,
                "offset": And(And(list, [int]), lambda o: len(o) == 2),
            }
        )
        area_centerimage = Schema(
            {
                "layer": "image",
                "file": str,
                "offset": And(And(list, [int]), lambda o: len(o) == 2),
            }
        )

        schemas = {
            "point": {
                "circle": point_circle,
                "text": point_text,
                "square": point_square,
                "image": point_image,
            },
            "line": {"text": line_text, "back": line_backfore, "fore": line_backfore},
            "area": {
                "bordertext": area_bordertext,
                "centertext": area_centertext,
                "fill": area_fill,
                "centerimage": area_centerimage,
            },
        }

        main_schema.validate(json)
        for n, t in json["types"].items():
            if n not in json["order"]:
                raise ValueError(f"Type {n} is not in order list")
            s = t["style"]
            for z, steps in s.items():
                if internal._str_to_tuple(z)[0] > internal._str_to_tuple(z)[1]:
                    raise ValueError(f"Invalid range '{z}'")
                for step in steps:
                    if not step["layer"] in schemas[t["type"]]:
                        raise ValueError(f"Invalid layer '{step}'")
                    else:
                        try:
                            schemas[t["type"]][step["layer"]].validate(step)
                        except Exception as e:
                            term = blessed.Terminal()
                            print(
                                term.red(f"Type {n}, range {z}, step {step['layer']}")
                            )
                            raise e
        return True
