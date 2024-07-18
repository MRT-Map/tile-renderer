from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Self, dataclass_transform

import msgspec
from msgspec import Struct, field

from tile_renderer.types.colour import Colour
from tile_renderer.types.coord import Vector

if TYPE_CHECKING:
    from pathlib import Path


@dataclass_transform()
class Skin(Struct):
    name: str
    fonts: dict[Literal["", "i", "b", "bi"], list[bytes]]
    background: Colour
    types: list[ComponentType]
    licence: str = ""

    def encode(self) -> _SerSkin:
        return _SerSkin(
            name=self.name,
            fonts=self.fonts,
            background=str(self.background),
            types=[t.encode() for t in self.types],
            licence=self.licence,
        )

    @classmethod
    def from_file(cls, file: Path) -> Self:
        """
        Load a skin file from a path, can be either in JSON or MessagePack format
        """
        if file.suffix == ".msgpack":
            return cls.from_msgpack(file)
        return cls.from_json(file)

    @classmethod
    def from_json(cls, file: Path) -> Self:
        """
        Load a skin file, must be in JSON
        """
        with file.open("rb") as f:
            b = f.read()
        return _json_decoder.decode(b).decode()

    @classmethod
    def from_msgpack(cls, file: Path) -> Self:
        """
        Load a skin file, must be in MessagePack
        """
        with file.open("rb") as f:
            b = f.read()
        return _msgpack_decoder.decode(b).decode()

    def save_json(self, directory: Path) -> None:
        """
        Save the skin file in JSON format to a directory
        """
        with (directory / f"{self.name}.skin.json").open("wb+") as f:
            f.write(_json_encoder.encode(self.encode()))

    def save_msgpack(self, directory: Path) -> None:
        """
        Save the skin file in MessagePack format to a directory
        """
        with (directory / f"{self.name}.skin.msgpack").open("wb+") as f:
            f.write(_msgpack_encoder.encode(self.encode()))


@dataclass_transform()
class _SerSkin(Skin):
    background: str
    types: list[_SerComponentType]

    def decode(self) -> Skin:
        return Skin(
            name=self.name,
            fonts=self.fonts,
            background=Colour.from_hex(self.background),
            types=[t.decode() for t in self.types],
            licence=self.licence,
        )


@dataclass_transform()
class ComponentType(Struct):
    name: str
    shape: Literal["point", "line", "area"]
    styles: dict[str, list[ComponentStyle]]
    tags: list[str] = field(default_factory=list)

    def encode(self) -> _SerComponentType:
        return _SerComponentType(
            name=self.name,
            tags=self.tags,
            shape=self.shape,
            styles={k: [s.encode() for s in v] for k, v in self.styles.items()},
        )


@dataclass_transform()
class _SerComponentType(ComponentType):
    styles: dict[str, list[_SerComponentStyle]]

    def decode(self) -> ComponentType:
        return ComponentType(
            name=self.name,
            tags=self.tags,
            shape=self.shape,
            styles={k: [s.decode() for s in v] for k, v in self.styles.items()},
        )


type ComponentStyle = (
    AreaBorderText
    | AreaCentreText
    | AreaFill
    | AreaCentreImage
    | LineText
    | LineFore
    | LineBack
    | PointText
    | PointSquare
    | PointImage
)
type _SerComponentStyle = (
    _SerAreaBorderText
    | _SerAreaCentreText
    | _SerAreaFill
    | _SerAreaCentreImage
    | _SerLineText
    | _SerLineFore
    | _SerLineBack
    | _SerPointText
    | _SerPointSquare
    | _SerPointImage
)


@dataclass_transform()
class AreaBorderText(Struct):
    size: int
    colour: Colour | None = None
    offset: int = 0

    def encode(self) -> _SerAreaBorderText:
        return _SerAreaBorderText(
            colour=None if self.colour is None else str(self.colour), offset=self.offset, size=self.size
        )


@dataclass_transform()
class _SerAreaBorderText(AreaBorderText, tag_field="ty", tag="areaBorderText"):
    colour: str | None = None

    def decode(self) -> AreaBorderText:
        return AreaBorderText(
            colour=None if self.colour is None else Colour.from_hex(self.colour), offset=self.offset, size=self.size
        )


@dataclass_transform()
class AreaCentreText(Struct):
    size: int
    colour: Colour | None = None
    offset: Vector[float] = Vector(0.0, 0.0)

    def encode(self) -> _SerAreaCentreText:
        return _SerAreaCentreText(
            colour=None if self.colour is None else str(self.colour), offset=self.offset.encode(), size=self.size
        )


@dataclass_transform()
class _SerAreaCentreText(AreaCentreText, tag_field="ty", tag="areaCentreText"):
    colour: str | None = None
    offset: tuple[float, float] = (0.0, 0.0)

    def decode(self) -> AreaCentreText:
        return AreaCentreText(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            offset=Vector.decode(self.offset),
            size=self.size,
        )


@dataclass_transform()
class AreaFill(Struct):
    colour: Colour | None = None
    outline: Colour | None = None

    # stripe: tuple[int, int, int] | None = None

    def encode(self) -> _SerAreaFill:
        return _SerAreaFill(
            colour=None if self.colour is None else str(self.colour),
            outline=None if self.outline is None else str(self.outline),
        )


@dataclass_transform()
class _SerAreaFill(AreaFill, tag_field="ty", tag="areaFill"):
    colour: str | None = None
    outline: str | None = None

    def decode(self) -> AreaFill:
        return AreaFill(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            outline=None if self.outline is None else Colour.from_hex(self.outline),
        )


@dataclass_transform()
class AreaCentreImage(Struct):
    image: bytes
    offset: Vector[float] = Vector(0.0, 0.0)

    def encode(self) -> _SerAreaCentreImage:
        return _SerAreaCentreImage(image=self.image, offset=self.offset.encode())


@dataclass_transform()
class _SerAreaCentreImage(AreaCentreImage, tag_field="ty", tag="areaCentreImage"):
    offset: tuple[float, float] = (0.0, 0.0)

    def decode(self) -> AreaCentreImage:
        return AreaCentreImage(image=self.image, offset=Vector.decode(self.offset))


@dataclass_transform()
class LineText(Struct):
    size: int
    arrow_colour: Colour | None = None
    colour: Colour | None = None
    offset: int = 0

    def encode(self) -> _SerLineText:
        return _SerLineText(
            arrow_colour=None if self.arrow_colour is None else str(self.arrow_colour),
            colour=None if self.colour is None else str(self.colour),
            size=self.size,
            offset=self.offset,
        )


@dataclass_transform()
class _SerLineText(LineText, tag_field="ty", tag="lineText"):
    arrow_colour: str | None = None
    colour: str | None = None

    def decode(self) -> LineText:
        return LineText(
            arrow_colour=None if self.arrow_colour is None else Colour.from_hex(self.arrow_colour),
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            size=self.size,
            offset=self.offset,
        )


@dataclass_transform()
class LineFore(Struct):
    width: int
    dash: list[int] | None = None
    colour: Colour | None = None

    def encode(self) -> _SerLineFore:
        return _SerLineFore(
            colour=None if self.colour is None else str(self.colour),
            width=self.width,
            dash=self.dash,
        )


@dataclass_transform()
class _SerLineFore(LineFore, tag_field="ty", tag="lineFore"):
    colour: str | None = None

    def decode(self) -> LineFore:
        return LineFore(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            width=self.width,
            dash=self.dash,
        )


@dataclass_transform()
class LineBack(LineFore):
    pass


@dataclass_transform()
class _SerLineBack(_SerLineFore, tag_field="ty", tag="lineBack"):
    pass


@dataclass_transform()
class PointText(Struct):
    anchor: str
    size: int
    colour: Colour | None = None
    offset: Vector[float] = Vector(0.0, 0.0)

    def encode(self) -> _SerPointText:
        return _SerPointText(
            colour=None if self.colour is None else str(self.colour),
            offset=self.offset.encode(),
            anchor=self.anchor,
            size=self.size,
        )


@dataclass_transform()
class _SerPointText(PointText, tag_field="ty", tag="pointText"):
    colour: str | None = None
    offset: tuple[float, float] = (0.0, 0.0)

    def decode(self) -> PointText:
        return PointText(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            offset=Vector.decode(self.offset),
            anchor=self.anchor,
            size=self.size,
        )


@dataclass_transform()
class PointSquare(Struct):
    size: int
    width: int
    colour: Colour | None = None
    outline: Colour | None = None
    border_radius: int = 0

    def encode(self) -> _SerPointSquare:
        return _SerPointSquare(
            colour=None if self.colour is None else str(self.colour),
            outline=None if self.outline is None else str(self.outline),
        )


@dataclass_transform()
class _SerPointSquare(PointSquare, tag_field="ty", tag="pointSquare"):
    colour: str | None = None
    outline: str | None = None

    def decode(self) -> PointSquare:
        return PointSquare(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            outline=None if self.outline is None else Colour.from_hex(self.outline),
        )


@dataclass_transform()
class PointImage(AreaCentreImage):
    pass


@dataclass_transform()
class _SerPointImage(_SerAreaCentreImage, tag_field="ty", tag="pointImage"):
    pass


_json_decoder = msgspec.json.Decoder(_SerSkin)
_msgpack_decoder = msgspec.msgpack.Decoder(_SerSkin)
_json_encoder = msgspec.json.Encoder()
_msgpack_encoder = msgspec.msgpack.Encoder()