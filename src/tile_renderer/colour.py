import colorsys
import dataclasses
from copy import copy
from typing import Self


@dataclasses.dataclass
class Colour:
    h: float
    s: float
    l: float

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float):
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        return cls(h * 360, s * 100, l * 100)

    @classmethod
    def from_hex(cls, h: int | str):
        if isinstance(h, int):
            r = h >> 16
            g = (h >> 8) & 0xFF
            b = h & 0xFF
        elif h.startswith("#"):
            if len(h) == 4:  # noqa: PLR2004
                r = int(h[1] * 2, 16)
                g = int(h[2] * 2, 16)
                b = int(h[3] * 2, 16)
            elif len(h) == 7:  # noqa: PLR2004
                r = int(h[1:3], 16)
                g = int(h[3:5], 16)
                b = int(h[5:7], 16)
            else:
                raise ValueError
        else:
            raise ValueError
        return cls.from_rgb(r, g, b)

    def __post_init__(self):
        if self.h < 0 or self.h > 360:  # noqa: PLR2004
            msg = f"h must be between 0 and 360, got {self.h}"
            raise ValueError(msg)
        if self.s < 0 or self.s > 100:  # noqa: PLR2004
            msg = f"s must be between 0 and 100, got {self.s}"
            raise ValueError(msg)
        if self.l < 0 or self.l > 100:  # noqa: PLR2004
            msg = f"l must be between 0 and 100, got {self.l}"
            raise ValueError(msg)

    def __str__(self) -> str:
        r, g, b = self.rgb
        return "#" + hex(round(r))[2:].zfill(2) + hex(round(g))[2:].zfill(2) + hex(round(b))[2:].zfill(2)

    @property
    def rgb(self) -> tuple[float, float, float]:
        r, g, b = colorsys.hls_to_rgb(self.h / 360, self.l / 100, self.s / 100)
        return 255 * r, 255 * g, 255 * b

    @property
    def r(self):
        return self.rgb[0]

    @r.setter
    def r(self, val: float):
        if val < 0 or val > 255:  # noqa: PLR2004
            msg = f"r must be between 0 and 255, got {val}"
            raise ValueError(msg)
        h, l, s = colorsys.rgb_to_hls(val / 255, self.g / 255, self.b / 255)
        self.h = h * 360
        self.l = l * 100
        self.s = s * 100

    @property
    def g(self):
        return self.rgb[1]

    @g.setter
    def g(self, val: float):
        if val < 0 or val > 255:  # noqa: PLR2004
            msg = f"g must be between 0 and 255, got {val}"
            raise ValueError(msg)
        h, l, s = colorsys.rgb_to_hls(self.r / 255, val / 255, self.b / 255)
        self.h = h * 360
        self.l = l * 100
        self.s = s * 100

    @property
    def b(self):
        return self.rgb[2]

    @b.setter
    def b(self, val: float):
        if val < 0 or val > 255:  # noqa: PLR2004
            msg = f"b must be between 0 and 255, got {val}"
            raise ValueError(msg)
        h, l, s = colorsys.rgb_to_hls(self.r / 255, self.g / 255, val / 255)
        self.h = h * 360
        self.l = l * 100
        self.s = s * 100

    def darkened(self, by: float = 30.0) -> Self:
        s = copy(self)
        s.l -= by
        if s.l < 0:
            s.l = 0
        return s

    def brightened(self, by: float = 30.0) -> Self:
        s = copy(self)
        s.l += by
        if s.l > 100:  # noqa: PLR2004
            s.l = 100
        return s
