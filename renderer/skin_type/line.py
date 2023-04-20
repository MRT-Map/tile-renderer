from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageDraw, ImageFont

from .. import math_utils
from .._internal import with_next
from ..misc_types.coord import ImageCoord, ImageLine, TileCoord
from ..render.text_object import TextObject
from . import ComponentStyle

if TYPE_CHECKING:
    from ..misc_types.config import Config
    from ..misc_types.pla2 import Component
    from ..render.part1 import Part1Consts


class LineText(ComponentStyle):
    """Represents text of a point"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        self.tags = tags
        self.layer = "text"
        self.arrow_colour: str | None = json["arrow_colour"]
        self.colour: str | None = json["colour"]
        self.size: int = json["size"]
        self.offset: int = json["offset"]

    @staticmethod
    def _text_on_line(
        size: int,
        colour: str | None,
        imd: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        text: str,
        zoom: int,
        coords: ImageLine,
        config: Config,
        fill: str | None = None,
        stroke: str | None = None,
        upright: bool = True,
    ) -> TextObject | None:
        char_cursor = 0
        text_to_print = ""
        overflow = 0
        text_objects = []
        swap = coords[-1].x < coords[0].x
        if swap and upright:
            coords = ImageLine(coords.coords[::-1])
        for c1, c2 in with_next(list(coords)):
            if c2 == coords[-1]:
                while char_cursor < len(text):
                    text_to_print += text[char_cursor]
                    char_cursor += 1
            else:
                while overflow + imd.textlength(
                    text_to_print,
                    font,
                ) < c1.point.distance(c2.point) and char_cursor < len(text):
                    text_to_print += text[char_cursor]
                    char_cursor += 1
            text_length = imd.textlength(text_to_print, font)

            if text_length != 0:
                lt_i = Image.new(
                    "RGBA",
                    (2 * int(text_length), 2 * (size + 4)),
                    (0, 0, 0, 0),
                )
                lt_d = ImageDraw.Draw(lt_i)
                lt_d.text(
                    (int(text_length), size + 4),
                    text_to_print,
                    fill=fill or colour,
                    font=font,
                    anchor="mm",
                    stroke_width=1,
                    stroke_fill=stroke or "#dddddd",
                    spacing=1,
                )
                trot = math.atan2(-c2.y + c1.y, c2.x - c1.x)
                lt_i = lt_i.rotate(trot * 180 / math.pi, expand=True)
                lt_i = lt_i.crop((0, 0, lt_i.width, lt_i.height))
                tx = c1.x - (-overflow / 2.5 - text_length / 2) * math.cos(trot)
                ty = c1.y + (-overflow / 2.5 - text_length / 2) * math.sin(trot)

                text_objects.append(
                    TextObject(
                        lt_i,
                        ImageCoord(tx, ty),
                        (text_length, size),
                        trot,
                        zoom,
                        config,
                    ),
                )

            text_to_print = " "
            overflow = (text_length - (c1.point.distance(c2.point) - overflow)) / 2

            if char_cursor >= len(text):
                break
        if text_objects:
            return TextObject.from_multiple(*text_objects)
        return None

    def render(
        self,
        component: Component,
        _: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ) -> None:
        if "oneWay" not in component.tags:
            return
        coords = component.nodes.to_image_line(tile_coord, consts)
        arrow_coord_lines = math_utils.dash(
            coords.parallel_offset(self.offset),
            self.size,
            self.size * 5,
        )
        ai = Image.new("RGBA", (self.size // 2,) * 2, (0,) * 4)
        ad = ImageDraw.Draw(ai)
        ad.polygon(
            [(0, 0), (0, self.size // 2), (self.size // 2, self.size // 2 / 2)],
            fill=self.arrow_colour,
        )
        for arrow_coord_line in arrow_coord_lines:
            if len(arrow_coord_line.coords) >= 2:
                c1 = arrow_coord_line.coords[0]
                c2 = arrow_coord_line.coords[1]
                rot = math.atan2(-c2.y + c1.y, c2.x - c1.x)
                nai = ai.rotate(rot * 180 / math.pi, expand=True)
                img.paste(
                    nai,
                    (int(c1.x - ai.width / 2), int(c1.y - ai.height / 2)),
                    nai,
                )

    def text(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        config: Config,
        zoom: int,
    ) -> list[TextObject]:
        coords = component.nodes.to_image_line(TileCoord(zoom, 0, 0), config)
        text_list: list[TextObject] = []
        if len(component.display_name) == 0:
            return []
        font = config.skin.get_font(
            "",
            self.size + 2,
            config.assets_dir,
            component.display_name,
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
                c1.point.distance(c2.point)
                for c1, c2 in with_next(list(coord_lines[-1]))
            )
            < text_length
        ):
            coord_lines = coord_lines[:-1]
        if os.environ.get("DEBUG"):
            imd.line(
                [c.as_tuple() for c in coords.parallel_offset(self.offset)],
                fill="#ff0000",
            )
        text_list.extend(
            e
            for e in (
                LineText._text_on_line(
                    self.size,
                    self.colour,
                    imd,
                    font,
                    component.display_name,
                    zoom,
                    cs,
                    config,
                )
                for cs in coord_lines
            )
            if e is not None
        )

        return text_list


class LineFore(ComponentStyle):
    """Represents the front layer of a line"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        self.tags = tags
        self.layer = "fore"
        self.colour: str | None = json["colour"]
        self.width: int = json["width"]
        self.dash: tuple[int, int] = json["dash"]

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        _: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ) -> None:
        coords = component.nodes.to_image_line(tile_coord, consts)
        if self.dash is None:
            imd.line(
                [c.as_tuple() for c in coords],
                fill=self.colour,
                width=self.width,
                joint="curve",
            )
            if "unroundedEnds" not in self.tags:
                try:
                    imd.ellipse(
                        [
                            coords[0].x - self.width / 2 + 1,
                            coords[0].y - self.width / 2 + 1,
                            coords[0].x + self.width / 2 - 1,
                            coords[0].y + self.width / 2 - 1,
                        ],
                        fill=self.colour,
                    )
                    imd.ellipse(
                        [
                            coords[-1].x - self.width / 2 + 1,
                            coords[-1].y - self.width / 2 + 1,
                            coords[-1].x + self.width / 2 - 1,
                            coords[-1].y + self.width / 2 - 1,
                        ],
                        fill=self.colour,
                    )
                except ValueError:
                    pass
        else:
            for dash_coords in math_utils.dash(coords, self.dash[0], self.dash[1]):
                imd.line(
                    [c.as_tuple() for c in dash_coords],
                    fill=self.colour,
                    width=self.width,
                )


class LineBack(LineFore):
    """Represent the back layer of a line"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        super().__init__(json, tags)
        self.layer = "back"
