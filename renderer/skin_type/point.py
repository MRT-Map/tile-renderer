from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageDraw

from ..misc_types.coord import ImageCoord, TileCoord
from ..render.text_object import TextObject
from ..skin_type import ComponentStyle

if TYPE_CHECKING:
    from ..misc_types.config import Config
    from ..misc_types.pla2 import Component
    from ..render.part1 import Part1Consts


class PointCircle(ComponentStyle):
    """Represents a circle of a point"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        self.tags = tags
        self.layer = "circle"
        self.colour: str | None = json["colour"]
        self.outline: str | None = json["outline"]
        self.size: int = json["size"]
        self.width: int = json["width"]

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        _: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ) -> None:
        coords = component.nodes.to_image_line(tile_coord, consts)
        coord = coords[0]
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
    """Represents a text of a point"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        self.tags = tags
        self.layer = "text"
        self.colour: str | None = json["colour"]
        self.size: int = json["size"]
        self.offset: ImageCoord = ImageCoord(*json["offset"])
        self.anchor: str = json["anchor"]

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ) -> None:
        pass

    def text(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        config: Config,
        zoom: int,
    ) -> list[TextObject]:
        coords = component.nodes.to_image_line(TileCoord(zoom, 0, 0), config)
        coord = coords[0]
        if len(component.display_name.strip()) == 0:
            return []
        font = config.skin.get_font(
            "",
            self.size + 2,
            config.assets_dir,
            component.display_name,
        )
        text_length = int(imd.textlength(component.display_name, font))
        pt_i = Image.new("RGBA", (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0))
        pt_d = ImageDraw.Draw(pt_i)
        pt_d.text(
            (text_length, self.size + 4),
            component.display_name,
            fill=self.colour,
            font=font,
            anchor="mm",
            stroke_width=1,
            stroke_fill="#dddddd",
            spacing=-self.size / 2,
        )
        pt_i = pt_i.crop((0, 0, pt_i.width, pt_i.height))
        return [
            TextObject(
                pt_i,
                ImageCoord(coord.x + self.offset.x, coord.y + self.offset.y),
                (text_length, self.size),
                0,
                zoom,
                config,
            ),
        ]


class PointSquare(ComponentStyle):
    """Represents a square of a point"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        self.tags = tags
        self.layer = "square"
        self.colour: str | None = json["colour"]
        self.outline: str | None = json["outline"]
        self.size: int = json["size"]
        self.width: int = json["width"]

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        _: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ) -> None:
        coords = component.nodes.to_image_line(tile_coord, consts)
        coord = coords[0]
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
    """Represents an image of a point"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_: Any, **__: Any) -> None:
        self.tags = tags
        self.layer = "image"
        self.file: Path = Path(json["file"])
        self.offset: ImageCoord = ImageCoord(*json["offset"])

    def render(
        self,
        component: Component,
        _: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ) -> None:
        coords = component.nodes.to_image_line(tile_coord, consts)
        coord = coords[0]
        icon = Image.open(consts.assets_dir / self.file)
        img.paste(
            icon,
            (
                int(coord.x - icon.width / 2 + self.offset.x),
                int(coord.y - icon.height / 2 + self.offset.y),
            ),
            icon,
        )
