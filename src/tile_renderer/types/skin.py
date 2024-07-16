from __future__ import annotations

from typing import Literal

from msgspec import Struct

from tile_renderer.types.colour import Colour
from tile_renderer.types.coord import Vector


class Skin(Struct):
    tile_size: int
    fonts: dict[Literal["", "i", "b", "bi"], list[bytes]]
    background: Colour
    types: ComponentType

    def encode(self) -> _SerSkin:
        return _SerSkin(
            tile_size=self.tile_size,
            fonts=self.fonts,
            background=str(self.background),
            types=self.types,
        )


class _SerSkin(Skin):
    background: str

    def decode(self) -> Skin:
        return Skin(
            tile_size=self.tile_size,
            fonts=self.fonts,
            background=Colour.from_hex(self.background),
            types=self.types,
        )


class ComponentType(Struct):
    name: str
    tags: list[str]
    shape: Literal["point", "line", "area"]
    styles: list[list[ComponentStyle]]


type ComponentStyle = AreaBorderText


class AreaBorderText(Struct):
    colour: Colour | None = None
    offset: int = 0
    size: int

    def encode(self) -> _SerAreaBorderText:
        return _SerAreaBorderText(
            colour=None if self.colour is None else str(self.colour), offset=self.offset, size=self.size
        )


class _SerAreaBorderText(AreaBorderText, tag_field="ty", tag=True):
    colour: str | None = None

    def decode(self) -> AreaBorderText:
        return AreaBorderText(
            colour=None if self.colour is None else Colour.from_hex(self.colour), offset=self.offset, size=self.size
        )


class AreaCentreText(Struct):
    colour: Colour | None = None
    offset: Vector[float] = Vector(0.0, 0.0)
    size: int

    def encode(self) -> _SerAreaCentreText:
        return _SerAreaCentreText(
            colour=None if self.colour is None else str(self.colour), offset=self.offset.encode(), size=self.size
        )


class _SerAreaCentreText(AreaCentreText, tag_field="ty", tag=True):
    colour: str | None = None
    offset: tuple[float, float] = (0.0, 0.0)

    def decode(self) -> AreaCentreText:
        return AreaCentreText(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            offset=Vector.decode(self.offset),
            size=self.size,
        )


class AreaFill(Struct):
    colour: Colour | None = None
    outline: Colour | None = None
    # stripe: tuple[int, int, int] | None = None


def encode(self) -> _SerAreaFill:
    return _SerAreaFill(
        colour=None if self.colour is None else str(self.colour),
        outline=None if self.outline is None else str(self.outline),
    )


class _SerAreaFill(AreaFill, tag_field="ty", tag=True):
    colour: str | None = None
    outline: str | None = None

    def decode(self) -> AreaFill:
        return AreaFill(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            outline=None if self.outline is None else Colour.from_hex(self.outline),
        )


class AreaCentreImage(Struct):
    image: bytes
    offset: Vector[float] = Vector(0.0, 0.0)
    # stripe: tuple[int, int, int] | None = None

    def encode(self) -> _SerAreaCentreImage:
        return _SerAreaCentreImage(image=self.image, offset=self.offset.encode())


class _SerAreaCentreImage(AreaCentreImage, tag_field="ty", tag=True):
    offset: tuple[float, float] = (0.0, 0.0)

    def decode(self) -> AreaCentreImage:
        return AreaCentreImage(image=self.image, offset=Vector.decode(self.offset))
