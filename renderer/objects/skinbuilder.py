from __future__ import annotations
from pathlib import Path
from typing import Literal

from renderer.types import Coord

def _hex_to_colour(h: int | None) -> str | None:
    if h is None: return None
    nh = hex(h)[2:]
    if len(nh) != 6: nh = nh.zfill(6)
    return "#"+nh

def _blend(h1: int, h2: int, prop: float = 0.5) -> int:
    nh1 = hex(h1)[2:].zfill(6)
    nh2 = hex(h2)[2:].zfill(6)
    r = hex(round(int(nh1[0:2], base=16)*(1-prop) + int(nh2[0:2], base=16)*prop))[2:].zfill(2)
    g = hex(round(int(nh1[2:4], base=16)*(1-prop) + int(nh2[2:4], base=16)*prop))[2:].zfill(2)
    b = hex(round(int(nh1[4:6], base=16)*(1-prop) + int(nh2[4:6], base=16)*prop))[2:].zfill(2)
    return int(r+g+b, base=16)

def _darken(h1: int, strength: float = 0.5) -> int:
    nh1 = hex(h1)[2:].zfill(6)
    r = int(nh1[0:2], base=16)/255
    g = int(nh1[2:4], base=16)/255
    b = int(nh1[4:6], base=16)/255
    k = 1-max(r, g, b)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)

    k += strength*(1-k)

    r = hex(round(255*(1-c)*(1-k)))[2:].zfill(2)
    g = hex(round(255*(1-m)*(1-k)))[2:].zfill(2)
    b = hex(round(255*(1-y)*(1-k)))[2:].zfill(2)
    return int(r + g + b, base=16)

def _lighten(h1: int, strength: float = 0.5) -> int:
    nh1 = hex(h1)[2:].zfill(6)
    r = int(nh1[0:2], base=16)/255
    g = int(nh1[2:4], base=16)/255
    b = int(nh1[4:6], base=16)/255
    cmin = min(r, g, b)
    cmax = max(r, g, b)
    delta = cmax - cmin
    h = 0 if delta == 0 \
        else 60*((g-b)/delta % 6) if cmax == r \
        else 60*((b-r)/delta + 2) if cmax == g \
        else 60*((r-g)/delta + 4)
    s = 0 if cmax == 0 else delta/cmax
    v = cmax

    s *= 1-strength

    c = v*s
    x = c*(1-abs(((h/60) % 2)-1))
    m = v-c
    r, g, b = (c, x, 0) if 0 <= h < 60 \
        else (x, c, 0) if 60 <= h < 120 \
        else (0, c, x) if 120 <= h < 180 \
        else (0, x, c) if 180 <= h < 240 \
        else (x, 0, c) if 240 <= h < 300 \
        else (c, 0, x)

    r = hex(round((r+m)*255))[2:].zfill(2)
    g = hex(round((g+m)*255))[2:].zfill(2)
    b = hex(round((b+m)*255))[2:].zfill(2)
    return int(r + g + b, base=16)

class SkinBuilder:
    """Utility class for building skins.

    :param int tile_size: Size of the tiles that the skin produces.
    :param fonts: Keys are the formatting, eg "", "b", "i", "bi", values are the relative paths to the fonts.
    :type fonts: dict[str, Path]
    :param int background: The colour of the background in hexadecimal."""
    tile_size: int
    fonts: dict[str, Path]
    background: str
    types: dict[str, ComponentTypeInfo]
    def __init__(self, tile_size: int, fonts: dict[str, Path], background: int):
        self.tile_size = tile_size
        self.fonts = fonts
        self.background = _hex_to_colour(background)
        self.types = {}

    def __setitem__(self, key: str, value: ComponentTypeInfo):
        self.types[key] = value

    def json(self) -> dict:
        """Returns a JSON representation of the skin.
        :rtype: dict"""
        return {
            "info": {
                "size": self.tile_size,
                "font": {k: str(v) for k, v in self.fonts.items()},
                "background": self.background
            },
            "order": list(self.types.keys()),
            "types": {k: v.json() for k, v in self.types.items()}
        }

    class ComponentTypeInfo:
        """Utility class for building the component type info for the skin.

        :param shape: The shape of the component. Must be either `point`, `line` or `area`.
        :type shape: str
        :param list[str] tags: A list of tags for the component"""
        shape: Literal["point", "line", "area"]
        tags: list[str]
        style: dict[str, list[ComponentStyle]]
        def __init__(self, shape: Literal["point", "line", "area"], tags: list[str] | None = None):
            self.shape = shape
            self.tags = tags or []
            self.style = {}

        def __setitem__(self, key: slice, value: list[ComponentStyle]):
            self.style[f"{key.start}, {key.stop or 1000}"] = value

        def json(self) -> dict:
            """Returns a JSON representation of the skin.
            :rtype: dict"""
            return {
                "tags": self.tags,
                "type": self.shape,
                "style": {k: [vv.json for vv in v] for k, v in self.style.items()}
            }

        class ComponentStyle:
            """Utility class for building the component style for the component."""
            json: dict
            @classmethod
            def point_circle(cls, *, colour: int | None = None,
                             outline: int | None = None,
                             size: int = 1,
                             width: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "circle",
                    "colour": _hex_to_colour(colour),
                    "outline": _hex_to_colour(outline),
                    "size": size,
                    "width": width
                }
                return cs

            @classmethod
            def point_text(cls, *, colour: int | None = None,
                           offset: Coord = Coord(0, 0),
                           size: int = 10,
                           anchor: str | None = None):
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": _hex_to_colour(colour),
                    "size": size,
                    "offset": offset,
                    "anchor": anchor
                }
                return cs

            @classmethod
            def point_square(cls, *, colour: int | None = None,
                             outline: int | None = None,
                             size: int = 1,
                             width: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "square",
                    "colour": _hex_to_colour(colour),
                    "outline": _hex_to_colour(outline),
                    "size": size,
                    "width": width
                }
                return cs

            @classmethod
            def point_image(cls, *, file: Path,
                            offset: Coord = Coord(0, 0)):
                cs = cls()
                cs.json = {
                    "layer": "image",
                    "file": str(file),
                    "offset": offset
                }
                return cs

            @classmethod
            def line_text(cls, *, colour: int | None = None,
                          arrow_colour: int | None = None,
                          size: int = 1,
                          offset: int = 0):
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": _hex_to_colour(colour),
                    "arrow_colour": _hex_to_colour(arrow_colour),
                    "size": size,
                    "offset": offset
                }
                return cs

            @classmethod
            def line_back(cls, *, colour: int | None = None,
                          width: int = 1,
                          dash: tuple[int, int] | None = None):
                cs = cls()
                cs.json = {
                    "layer": "back",
                    "colour": _hex_to_colour(colour),
                    "width": width,
                    "dash": dash
                }
                return cs

            @classmethod
            def line_fore(cls, *, colour: int | None = None,
                          width: int = 1,
                          dash: tuple[int, int] | None = None):
                cs = cls()
                cs.json = {
                    "layer": "fore",
                    "colour": _hex_to_colour(colour),
                    "width": width,
                    "dash": dash
                }
                return cs

            @classmethod
            def area_bordertext(cls, *, colour: int | None = None,
                                offset: int = 0,
                                size: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "bordertext",
                    "colour": _hex_to_colour(colour),
                    "offset": offset,
                    "size": size
                }
                return cs

            @classmethod
            def area_centertext(cls, *, colour: int | None = None,
                                size: int = 1,
                                offset: Coord = Coord(0, 0)):
                cs = cls()
                cs.json = {
                    "layer": "centertext",
                    "colour": _hex_to_colour(colour),
                    "offset": offset,
                    "size": size
                }
                return cs

            @classmethod
            def area_fill(cls, *,
                          colour: int | None = None,
                          outline: int | None = None,
                          stripe: tuple[int, int, int] | None = None):
                cs = cls()
                cs.json = {
                    "layer": "fill",
                    "colour": _hex_to_colour(colour),
                    "outline": _hex_to_colour(outline),
                    "stripe": stripe
                }
                return cs

            @classmethod
            def area_centerimage(cls, *, file: Path,
                                 offset: Coord = Coord(0, 0)):
                cs = cls()
                cs.json = {
                    "layer": "centerimage",
                    "file": str(file),
                    "offset": offset
                }
                return cs
CTI = SkinBuilder.ComponentTypeInfo
CS = SkinBuilder.ComponentTypeInfo.ComponentStyle