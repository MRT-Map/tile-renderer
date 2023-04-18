from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from schema import And, Optional, Or, Regex, Schema

from .._internal import read_json, str_to_tuple
from ..misc_types import SkinJson, SkinType

if TYPE_CHECKING:
    from ..render.part1 import Part1Consts
    from ..misc_types.pla2 import Component

from ..misc_types.coord import TileCoord

Image.Image.__hash__ = lambda self: int(str(imagehash.average_hash(self)), base=16)  # type: ignore


class Skin:
    """Represents a skin.

    :param SkinJson json: The JSON of the skin.
    """

    def __init__(self, json: SkinJson):
        self.validate_json(json)
        self.tile_size: int = json["info"]["size"]
        self.fonts: dict[str, list[Path]] = {
            name: [Path(path) for path in paths]
            for name, paths in json["info"]["font"].items()
        }
        self.background: str = json["info"]["background"]

        self.order: list[str] = json["order"]
        self.types: dict[str, ComponentTypeInfo] = {
            name: ComponentTypeInfo(name, value, self.order)
            for name, value in json["types"].items()
        }

    def __getitem__(self, type_name: str) -> ComponentTypeInfo:
        return self.types[type_name]

    # @methodtools.lru_cache()
    def get_font(
        self, style: str, size: int, assets_dir: Path, rendered_text: str = ""
    ) -> ImageFont.FreeTypeFont:
        """Gets a font, given the style and size.

        :param str style: The style of the font needed, eg.
            bold, italic etc.
        :param int size: The size of the font
        :param Path assets_dir: Where the font is stored
        :param str rendered_text: The text that is rendered with the font, to allow for fallbacks
        :return: The font
        :raises FileNotFoundError: if font is not found"""
        if style in self.fonts.keys():
            pil_font = None
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
                if pil_font is None:
                    raise FileNotFoundError(f"Font for {style} not found")
                return pil_font
        raise FileNotFoundError(f"Font for {style} not found")

    @classmethod
    def from_name(cls, name: str = "default") -> Skin:
        """
        Gets a skin from inside the package.

        :param str name: the name of the skin

        :returns: The skin

        :raises FileNotFoundError: if skin does not exist
        """

        try:
            return cls(
                read_json(Path(__file__).parent.parent / "skins" / (name + ".json"))
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Skin '{name}' not found")

    @staticmethod
    def validate_json(json: SkinJson) -> Literal[True]:
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
                        "type": lambda t_: t_ in ("point", "line", "area"),
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
        line_back_fore = Schema(
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
            "line": {"text": line_text, "back": line_back_fore, "fore": line_back_fore},
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
                if str_to_tuple(z)[0] > str_to_tuple(z)[1]:
                    raise ValueError(f"Invalid range '{z}'")
                for step in steps:
                    if not step["layer"] in schemas[t["type"]]:
                        raise ValueError(f"Invalid layer '{step}'")
                    else:
                        try:
                            schemas[t["type"]][step["layer"]].validate(step)
                        except Exception as e:
                            raise type(e)(
                                "Error at type {n}, range {z}, step {step['layer']}"
                            ) from e
        return True


class ComponentTypeInfo:
    """An object representing a component type in the ``types`` portion of a skin.

    :param str name: Will set ``name``
    :param SkinType json: The JSON of the component type
    :param list[str] order: Will set ``_order``
    """

    def __init__(self, name: str, json: SkinType, order: list[str]):
        self.name: str = name
        """The name of the component."""
        self.tags: list[str] = json["tags"]
        """The list of tags attributed to the component."""
        self.shape: Literal["point", "line", "area"] = json["type"]
        """The shape of the component, must be one of ``point``, ``line``, ``area``"""
        self._order = order
        self.styles: dict[tuple[int, int], list[ComponentStyle]] = {
            str_to_tuple(range_): [  # type: ignore
                ComponentStyle(v, self.tags, self.shape) for v in value
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
    :param ComponentTypeInfo type_info: The type_info that the ComponentStyle is under
    """
    layer: str

    def __new__(
        cls,
        json: dict | None = None,
        tags: list[str] | None = None,
        shape: Literal["point", "line", "area"] | None = None,
    ):
        from .area import AreaBorderText, AreaCenterImage, AreaCenterText, AreaFill
        from .line import LineBack, LineFore, LineText
        from .point import PointCircle, PointImage, PointSquare, PointText

        if cls != ComponentStyle:
            return super().__new__(cls)
        json = json or {}
        if shape == "point":
            if json["layer"] == "circle":
                return PointCircle.__new__(PointCircle, json, tags)
            if json["layer"] == "text":
                return PointText.__new__(PointText, json, tags)
            if json["layer"] == "square":
                return PointSquare.__new__(PointSquare, json, tags)
            if json["layer"] == "image":
                return PointImage.__new__(PointImage, json, tags)
        elif shape == "line":
            if json["layer"] == "text":
                return LineText.__new__(LineText, json, tags)
            if json["layer"] == "back":
                return LineBack.__new__(LineBack, json, tags)
            if json["layer"] == "fore":
                return LineFore.__new__(LineFore, json, tags)
        elif shape == "area":
            if json["layer"] == "bordertext":
                return AreaBorderText.__new__(AreaBorderText, json, tags)
            if json["layer"] == "centertext":
                return AreaCenterText.__new__(AreaCenterText, json, tags)
            if json["layer"] == "fill":
                return AreaFill.__new__(AreaFill, json, tags)
            if json["layer"] == "centerimage":
                return AreaCenterImage.__new__(AreaCenterImage, json, tags)
        raise ValueError(f"No layer `{json['layer']}` in shape `{shape}`")

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ):
        """Renders the component into an ImageDraw instance."""