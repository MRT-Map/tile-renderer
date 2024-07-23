from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, dataclass_transform

import msgspec
from msgspec import Struct, field

from tile_renderer.colour import Colour
from tile_renderer.coord import Vector

if TYPE_CHECKING:
    import svg
    from shapely import Polygon

    from tile_renderer.pla2 import Component


@dataclass_transform()
class Skin(Struct):
    name: str
    types: list[ComponentType]
    font_files: list[tuple[str, bytes]]
    font_string: str = ""
    background: Colour = Colour.from_hex(0xFFFFFF)
    prune_small_text: float | None = None
    licence: str = ""

    def encode(self) -> _SerSkin:
        return _SerSkin(
            name=self.name,
            font_files=self.font_files,
            font_string=self.font_string,
            background=str(self.background),
            prune_small_text=self.prune_small_text,
            types=[t.encode() for t in self.types],
            licence=self.licence,
        )

    @classmethod
    def default(cls) -> Self:
        return cls.from_json(Path(__file__).parent / "default.skin.json")

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

    def get_type_by_name(self, name: str) -> ComponentType | None:
        return next((t for t in self.types if t.name == name), None)

    def get_order(self, name: str) -> int | None:
        return next((i for i, t in enumerate(self.types) if t.name == name), None)


@dataclass_transform()
class _SerSkin(Skin):
    types: list[_SerComponentType]
    background: str = "#ff0000"

    def decode(self) -> Skin:
        return Skin(
            name=self.name,
            font_files=self.font_files,
            font_string=self.font_string,
            background=Colour.from_hex(self.background),
            prune_small_text=self.prune_small_text,
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

    def get_styling_by_zoom(self, zoom: int) -> list[ComponentStyle] | None:
        for z, styling in self.styles.items():
            min_z = z.split("-")[0]
            min_z = 0 if min_z == "" else int(min_z)
            max_z = z.split("-")[-1]
            max_z = float("inf") if max_z == "" else int(max_z)
            if min_z <= zoom <= max_z:
                return [s.scale(zoom - min_z) for s in styling]
        return None


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


@dataclass_transform()
class ComponentStyle(Struct, kw_only=True):
    zoom_multiplier: float = 1.5

    def encode(self) -> Any:
        raise NotImplementedError

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        raise NotImplementedError

    def scale(self, zoom: int) -> Self:
        raise NotImplementedError


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
class AreaBorderText(ComponentStyle):
    size: int | float
    colour: Colour | None = None
    offset: int | float = 0

    def encode(self) -> _SerAreaBorderText:
        return _SerAreaBorderText(
            colour=None if self.colour is None else str(self.colour),
            offset=self.offset,
            size=self.size,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.area_border_text_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int):
        return AreaBorderText(
            size=self.size / self.zoom_multiplier**zoom,
            colour=self.colour,
            offset=self.offset / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerAreaBorderText(AreaBorderText, tag_field="ty", tag="areaBorderText"):
    colour: str | None = None

    def decode(self) -> AreaBorderText:
        return AreaBorderText(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            offset=self.offset,
            size=self.size,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class AreaCentreText(ComponentStyle):
    size: int | float
    colour: Colour | None = None
    offset: Vector[float] = Vector(0.0, 0.0)

    def encode(self) -> _SerAreaCentreText:
        return _SerAreaCentreText(
            colour=None if self.colour is None else str(self.colour),
            offset=self.offset.encode(),
            size=self.size,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.area_centre_text_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return AreaCentreText(
            size=self.size / self.zoom_multiplier**zoom,
            colour=self.colour,
            offset=self.offset / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
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
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class AreaFill(ComponentStyle):
    colour: Colour | None = None
    outline: Colour | None = None
    outline_width: int | float = 0

    # stripe: tuple[int, int, int] | None = None

    def encode(self) -> _SerAreaFill:
        return _SerAreaFill(
            colour=None if self.colour is None else str(self.colour),
            outline=None if self.outline is None else str(self.outline),
            outline_width=self.outline_width,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.area_fill_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return AreaFill(
            colour=self.colour,
            outline=self.outline,
            outline_width=self.outline_width / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerAreaFill(AreaFill, tag_field="ty", tag="areaFill"):
    colour: str | None = None
    outline: str | None = None

    def decode(self) -> AreaFill:
        return AreaFill(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            outline=None if self.outline is None else Colour.from_hex(self.outline),
            outline_width=self.outline_width,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class AreaCentreImage(ComponentStyle):
    image: bytes
    offset: Vector[float] = Vector(0.0, 0.0)

    def encode(self) -> _SerAreaCentreImage:
        return _SerAreaCentreImage(image=self.image, offset=self.offset.encode(), zoom_multiplier=self.zoom_multiplier)

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.area_centre_image_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return AreaCentreImage(
            image=self.image,
            offset=self.offset / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerAreaCentreImage(AreaCentreImage, tag_field="ty", tag="areaCentreImage"):
    offset: tuple[float, float] = (0.0, 0.0)

    def decode(self) -> AreaCentreImage:
        return AreaCentreImage(
            image=self.image, offset=Vector.decode(self.offset), zoom_multiplier=self.zoom_multiplier
        )


@dataclass_transform()
class LineText(ComponentStyle):
    size: int | float
    arrow_colour: Colour | None = None
    colour: Colour | None = None
    offset: int | float = 0

    def encode(self) -> _SerLineText:
        return _SerLineText(
            arrow_colour=None if self.arrow_colour is None else str(self.arrow_colour),
            colour=None if self.colour is None else str(self.colour),
            size=self.size,
            offset=self.offset,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.line_text_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return LineText(
            size=self.size / self.zoom_multiplier**zoom,
            arrow_colour=self.arrow_colour,
            colour=self.colour,
            offset=self.offset / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
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
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class LineFore(ComponentStyle):
    width: int | float
    dash: list[int | float] | None = None
    colour: Colour | None = None
    unrounded: bool = False

    def encode(self) -> _SerLineFore:
        return _SerLineFore(
            colour=None if self.colour is None else str(self.colour),
            width=self.width,
            dash=self.dash,
            unrounded=self.unrounded,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.line_back_fore_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return LineFore(
            width=self.width / self.zoom_multiplier**zoom,
            dash=[a / self.zoom_multiplier**zoom for a in self.dash] if self.dash is not None else None,
            colour=self.colour,
            unrounded=self.unrounded,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerLineFore(LineFore, tag_field="ty", tag="lineFore"):
    colour: str | None = None

    def decode(self) -> LineFore:
        return LineFore(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            width=self.width,
            dash=self.dash,
            unrounded=self.unrounded,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class LineBack(LineFore):
    def encode(self) -> _SerLineBack:
        return _SerLineBack(
            colour=None if self.colour is None else str(self.colour),
            width=self.width,
            dash=self.dash,
            unrounded=self.unrounded,
            zoom_multiplier=self.zoom_multiplier,
        )

    def scale(self, zoom: int) -> Self:
        return LineBack(
            width=self.width / self.zoom_multiplier**zoom,
            dash=[a / self.zoom_multiplier**zoom for a in self.dash] if self.dash is not None else None,
            colour=self.colour,
            unrounded=self.unrounded,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerLineBack(_SerLineFore, tag_field="ty", tag="lineBack"):
    def decode(self) -> LineBack:
        return LineBack(
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            width=self.width,
            dash=self.dash,
            unrounded=self.unrounded,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class PointText(ComponentStyle):
    anchor: str
    size: int | float
    colour: Colour | None = None
    offset: Vector[float] = Vector(0.0, 0.0)

    def encode(self) -> _SerPointText:
        return _SerPointText(
            colour=None if self.colour is None else str(self.colour),
            offset=self.offset.encode(),
            anchor=self.anchor,
            size=self.size,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.point_text_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return PointText(
            anchor=self.anchor,
            size=self.size / self.zoom_multiplier**zoom,
            colour=self.colour,
            offset=self.offset / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
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
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class PointSquare(ComponentStyle):
    size: int | float
    width: int | float
    colour: Colour | None = None
    outline: Colour | None = None
    border_radius: int | float = 0

    def encode(self) -> _SerPointSquare:
        return _SerPointSquare(
            size=self.size,
            width=self.width,
            colour=None if self.colour is None else str(self.colour),
            outline=None if self.outline is None else str(self.outline),
            border_radius=self.border_radius,
            zoom_multiplier=self.zoom_multiplier,
        )

    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.point_square_svg(self, component, zoom, text_list, skin)

    def scale(self, zoom: int) -> Self:
        return PointSquare(
            size=self.size / self.zoom_multiplier**zoom,
            width=self.width / self.zoom_multiplier**zoom,
            colour=self.colour,
            outline=self.outline,
            border_radius=self.border_radius / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerPointSquare(PointSquare, tag_field="ty", tag="pointSquare"):
    colour: str | None = None
    outline: str | None = None

    def decode(self) -> PointSquare:
        return PointSquare(
            size=self.size,
            width=self.width,
            colour=None if self.colour is None else Colour.from_hex(self.colour),
            outline=None if self.outline is None else Colour.from_hex(self.outline),
            border_radius=self.border_radius,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class PointImage(AreaCentreImage):
    def render(
        self,
        component: Component,
        zoom: int,
        text_list: list[tuple[Polygon, svg.Element]],
        skin: Skin,
    ) -> svg.Element:
        from tile_renderer import component_to_svg

        return component_to_svg.point_image_svg(self, component, zoom, text_list, skin)

    def encode(self) -> _SerPointImage:
        return _SerPointImage(image=self.image, offset=self.offset.encode(), zoom_multiplier=self.zoom_multiplier)

    def scale(self, zoom: int) -> Self:
        return PointImage(
            image=self.image,
            offset=self.offset / self.zoom_multiplier**zoom,
            zoom_multiplier=self.zoom_multiplier,
        )


@dataclass_transform()
class _SerPointImage(_SerAreaCentreImage, tag_field="ty", tag="pointImage"):
    def decode(self) -> PointImage:
        return PointImage(image=self.image, offset=Vector.decode(self.offset), zoom_multiplier=self.zoom_multiplier)


_json_decoder = msgspec.json.Decoder(_SerSkin)
_msgpack_decoder = msgspec.msgpack.Decoder(_SerSkin)
_json_encoder = msgspec.json.Encoder()
_msgpack_encoder = msgspec.msgpack.Encoder()
