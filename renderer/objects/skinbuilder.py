from __future__ import annotations
from pathlib import Path
from typing import Literal

from renderer.types import Coord


class SkinBuilder:
    tile_size: int
    fonts: dict[str, Path]
    background: str
    types: dict[str, ComponentTypeInfo]
    def __init__(self, tile_size: int, fonts: dict[str, Path], background: str):
        self.tile_size = tile_size
        self.fonts = fonts
        self.background = background

    def __setitem__(self, key: str, value: ComponentTypeInfo):
        self.types[key] = value

    class ComponentTypeInfo:
        shape: Literal["point", "line", "area"]
        tags: list[str]
        style: dict[slice, list[ComponentStyle]]
        def __init__(self, shape: Literal["point", "line", "area"], tags: list[str] | None = None):
            self.shape = shape
            self.tags = tags or []

        def __setitem__(self, key: slice, value: list[ComponentStyle]):
            self.style[key] = value

        class ComponentStyle:
            json: dict
            @classmethod
            def point_circle(cls, *, colour: str | None = None,
                             outline: str | None = None,
                             size: int = 1,
                             width: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "circle",
                    "colour": colour,
                    "outline": outline,
                    "size": size,
                    "width": width
                }
                return cs

            @classmethod
            def point_text(cls, *, colour: str | None = None,
                           offset: Coord = Coord(0, 0),
                           size: int = 10,
                           anchor: str | None = None):
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": colour,
                    "size": size,
                    "offset": offset or Coord(0, 0),
                    "anchor": anchor
                }
                return cs

            @classmethod
            def point_square(cls, *, colour: str | None = None,
                             outline: str | None = None,
                             size: int = 1,
                             width: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "square",
                    "colour": colour,
                    "outline": outline,
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
                    "file": file,
                    "offset": offset
                }
                return cs

            @classmethod
            def line_text(cls, *, colour: str | None = None,
                          size: int = 1,
                          offset: int = 0):
                cs = cls()
                cs.json = {
                    "layer": "text",
                    "colour": colour,
                    "size": size
                    "offset": offset
                }
                return cs

            @classmethod
            def line_back(cls, *, colour: str | None = None,
                          size: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "back",
                    "colour": colour,
                    "size": size
                }
                return cs

            @classmethod
            def line_fore(cls, *, colour: str | None = None,
                          size: int = 1):
                cs = cls()
                cs.json = {
                    "layer": "fore",
                    "colour": colour,
                    "size": size
                }
                return cs