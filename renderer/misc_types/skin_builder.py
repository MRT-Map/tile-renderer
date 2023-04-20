from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    from pathlib import Path


@overload
def hex_to_colour(h: int) -> str:
    pass


@overload
def hex_to_colour(h: None) -> None:
    pass


def hex_to_colour(h: int | None) -> str | None:
    """
    Converts a hex colour, represented as an integer, into a string of format ``#XXXXXX``
    :param h: The hex code (``0xXXXXXX``)
    """
    if h is None:
        return None
    nh = hex(h)[2:]
    if len(nh) != 6:
        nh = nh.zfill(6)
    return "#" + nh


def blend(h1: int, h2: int, prop: float = 0.5) -> int:
    """
    Blend two colours together

    :param h1: The first colour
    :param h2: The second colour
    :param prop: The proportion of the second colour, between 0.0 and 1.0
    """
    nh1 = hex(h1)[2:].zfill(6)
    nh2 = hex(h2)[2:].zfill(6)
    r = hex(round(int(nh1[0:2], base=16) * (1 - prop) + int(nh2[0:2], base=16) * prop))[
        2:
    ].zfill(2)
    g = hex(round(int(nh1[2:4], base=16) * (1 - prop) + int(nh2[2:4], base=16) * prop))[
        2:
    ].zfill(2)
    b = hex(round(int(nh1[4:6], base=16) * (1 - prop) + int(nh2[4:6], base=16) * prop))[
        2:
    ].zfill(2)
    return int(r + g + b, base=16)


def darken(h1: int, strength: float = 0.5) -> int:
    """
    Darken a colour

    :param h1: The colour
    :param strength: The strength of the darkening, between 0.0 and 1.0
    """
    nh1 = hex(h1)[2:].zfill(6)
    r = int(nh1[0:2], base=16) / 255
    g = int(nh1[2:4], base=16) / 255
    b = int(nh1[4:6], base=16) / 255
    k = 1 - max(r, g, b)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)

    k += strength * (1 - k)

    nr = hex(round(255 * (1 - c) * (1 - k)))[2:].zfill(2)
    ng = hex(round(255 * (1 - m) * (1 - k)))[2:].zfill(2)
    nb = hex(round(255 * (1 - y) * (1 - k)))[2:].zfill(2)
    return int(nr + ng + nb, base=16)


def brighten(h1: int, strength: float = 0.5) -> int:
    """
    Lighten a colour

    :param h1: The colour
    :param strength: The strength of the brightening, between 0.0 and 1.0
    """
    nh1 = hex(h1)[2:].zfill(6)
    r = int(nh1[0:2], base=16) / 255
    g = int(nh1[2:4], base=16) / 255
    b = int(nh1[4:6], base=16) / 255
    c_min = min(r, g, b)
    c_max = max(r, g, b)
    delta = c_max - c_min
    h = (
        0
        if delta == 0
        else 60 * ((g - b) / delta % 6)
        if c_max == r
        else 60 * ((b - r) / delta + 2)
        if c_max == g
        else 60 * ((r - g) / delta + 4)
    )
    s = 0 if c_max == 0 else delta / c_max
    v = c_max

    s *= 1 - strength

    c = v * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
    m = v - c
    r, g, b = (
        (c, x, 0)
        if 0 <= h < 60
        else (x, c, 0)
        if 60 <= h < 120
        else (0, c, x)
        if 120 <= h < 180
        else (0, x, c)
        if 180 <= h < 240
        else (x, 0, c)
        if 240 <= h < 300
        else (c, 0, x)
    )

    nr = hex(round((r + m) * 255))[2:].zfill(2)
    ng = hex(round((g + m) * 255))[2:].zfill(2)
    nb = hex(round((b + m) * 255))[2:].zfill(2)
    return int(nr + ng + nb, base=16)


class SkinBuilder:
    """Utility class for building skins."""

    tile_size: int
    """Size of the tiles that the skin produces."""
    fonts: dict[str, list[Path]]
    """Keys are the formatting, eg "", "b", "i", "bi", values are the relative paths to the fonts."""
    background: str
    """The colour of the background in hexadecimal."""
    types: dict[str, CTI]
    """The component types that have been registered."""

    def __init__(
        self,
        tile_size: int,
        fonts: dict[str, list[Path]],
        background: int,
    ) -> None:
        self.tile_size = tile_size
        self.fonts = fonts
        self.background = hex_to_colour(background) or "#000000"
        self.types = {}

    def __setitem__(self, key: str, value: CTI) -> None:
        print("Setting", key)
        self.types[key] = value

    def json(self) -> dict:
        """
        Returns a JSON representation of the skin.
        """
        return {
            "info": {
                "size": self.tile_size,
                "font": {k: [str(sv) for sv in v] for k, v in self.fonts.items()},
                "background": self.background,
            },
            "order": list(self.types.keys()),
            "types": {k: v.json() for k, v in self.types.items()},
        }

    class ComponentTypeInfo:
        """Utility class for building the component type info for the skin."""

        shape: Literal["point", "line", "area"]
        """The shape of the component. Must be either `point`, `line` or `area`."""
        tags: list[str]
        """A list of tags for the component"""
        style: dict[str, list[CS]]
        """The registered styles for the component type information"""

        def __init__(
            self,
            shape: Literal["point", "line", "area"],
            tags: list[str] | None = None,
        ) -> None:
            self.shape = shape
            self.tags = tags or []
            self.style = {}

        def __setitem__(self, key: int | slice, value: list[CS]) -> None:
            if isinstance(key, int):
                self.style[f"{key}, {key}"] = value
            else:
                self.style[f"{key.start}, {key.stop or 1000}"] = value

        def json(self) -> dict:
            """Returns a JSON representation of the skin."""
            return {
                "tags": self.tags,
                "type": self.shape,
                "style": {k: [vv.json for vv in v] for k, v in self.style.items()},
            }

        class ComponentStyle:
            """Utility class for building the component style for the component."""

            json: dict

            @classmethod
            def point_circle(
                cls,
                *,
                colour: int | None = None,
                outline: int | None = None,
                size: int = 1,
                width: int = 1,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "circle",
                    "colour": hex_to_colour(colour),
                    "outline": hex_to_colour(outline),
                    "size": size,
                    "width": width,
                }
                return cs

            @classmethod
            def point_text(
                cls,
                *,
                colour: int | None = None,
                offset: tuple[int, int] = (0, 0),
                size: int = 10,
                anchor: str | None = None,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": hex_to_colour(colour),
                    "size": size,
                    "offset": offset,
                    "anchor": anchor,
                }
                return cs

            @classmethod
            def point_square(
                cls,
                *,
                colour: int | None = None,
                outline: int | None = None,
                size: int = 1,
                width: int = 1,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "square",
                    "colour": hex_to_colour(colour),
                    "outline": hex_to_colour(outline),
                    "size": size,
                    "width": width,
                }
                return cs

            @classmethod
            def point_image(cls, *, file: Path, offset: tuple[int, int] = (0, 0)) -> CS:
                cs = cls()
                cs.json = {"layer": "image", "file": str(file), "offset": offset}
                return cs

            @classmethod
            def line_text(
                cls,
                *,
                colour: int | None = None,
                arrow_colour: int | None = None,
                size: int = 1,
                offset: int = 0,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": hex_to_colour(colour),
                    "arrow_colour": hex_to_colour(arrow_colour),
                    "size": size,
                    "offset": offset,
                }
                return cs

            @classmethod
            def line_back(
                cls,
                *,
                colour: int | None = None,
                width: int = 1,
                dash: tuple[int, int] | None = None,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "back",
                    "colour": hex_to_colour(colour),
                    "width": width,
                    "dash": dash,
                }
                return cs

            @classmethod
            def line_fore(
                cls,
                *,
                colour: int | None = None,
                width: int = 1,
                dash: tuple[int, int] | None = None,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "fore",
                    "colour": hex_to_colour(colour),
                    "width": width,
                    "dash": dash,
                }
                return cs

            @classmethod
            def area_bordertext(
                cls,
                *,
                colour: int | None = None,
                offset: int = 0,
                size: int = 1,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "bordertext",
                    "colour": hex_to_colour(colour),
                    "offset": offset,
                    "size": size,
                }
                return cs

            @classmethod
            def area_centertext(
                cls,
                *,
                colour: int | None = None,
                size: int = 1,
                offset: tuple[int, int] = (0, 0),
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "centertext",
                    "colour": hex_to_colour(colour),
                    "offset": offset,
                    "size": size,
                }
                return cs

            @classmethod
            def area_fill(
                cls,
                *,
                colour: int | None = None,
                outline: int | None = None,
                stripe: tuple[int, int, int] | None = None,
            ) -> CS:
                cs = cls()
                cs.json = {
                    "layer": "fill",
                    "colour": hex_to_colour(colour),
                    "outline": hex_to_colour(outline),
                    "stripe": stripe,
                }
                return cs

            @classmethod
            def area_centerimage(
                cls,
                *,
                file: Path,
                offset: tuple[int, int] = (0, 0),
            ) -> CS:
                cs = cls()
                cs.json = {"layer": "centerimage", "file": str(file), "offset": offset}
                return cs


CTI = SkinBuilder.ComponentTypeInfo
CS = CTI.ComponentStyle
