from __future__ import annotations
from pathlib import Path
from typing import Literal

from renderer.types import Coord

def _hex_to_colour(h: int | None) -> str | None:
    if h is None: return None
    nh = hex(h)[2:]
    if len(nh) != 6: nh = nh.zfill(6)
    return "#"+nh

class SkinBuilder:
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
            return {
                "tags": self.tags,
                "type": self.shape,
                "style": {k: [vv.json for vv in v] for k, v in self.style.items()}
            }

        class ComponentStyle:
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
                          size: int = 1,
                          offset: int = 0):
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": _hex_to_colour(colour),
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