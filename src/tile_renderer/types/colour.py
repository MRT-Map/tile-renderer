import colorsys
import dataclasses


@dataclasses.dataclass
class Colour:
    h: float
    s: float
    l: float

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float):
        h, l, s = colorsys.rgb_to_hls(r / 256, g / 256, b / 256)
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

    def __str__(self) -> str:
        r, g, b = self.rgb
        return "#" + hex(round(r))[2:].zfill(2) + hex(round(r))[2:].zfill(2) + hex(round(r))[2:].zfill(2)

    @property
    def rgb(self) -> tuple[float, float, float]:
        r, g, b = colorsys.hls_to_rgb(self.h / 360, self.l / 100, self.s / 100)
        return 256 * r, 256 * g, 256 * b

    @property
    def r(self):
        return self.rgb[0]

    @r.setter
    def r(self, val: float):
        h, l, s = colorsys.rgb_to_hls(val / 256, self.g / 256, self.b / 256)
        self.h = h * 360
        self.l = l * 100
        self.s = s * 100

    @property
    def g(self):
        return self.rgb[1]

    @g.setter
    def g(self, val: float):
        h, l, s = colorsys.rgb_to_hls(self.r / 256, val / 256, self.b / 256)
        self.h = h * 360
        self.l = l * 100
        self.s = s * 100

    @property
    def b(self):
        return self.rgb[2]

    @b.setter
    def b(self, val: float):
        h, l, s = colorsys.rgb_to_hls(self.r / 256, self.g / 256, val / 256)
        self.h = h * 360
        self.l = l * 100
        self.s = s * 100
