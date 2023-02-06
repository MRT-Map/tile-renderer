from __future__ import annotations

import functools
import math
from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, Any, Generator, Generic, NamedTuple, TypeVar

from shapely.geometry import LineString, Point  # type: ignore

from .. import math_utils
from .._internal import with_next

if TYPE_CHECKING:
    from .skin import Skin

from .zoom_params import ZoomParams

_T = TypeVar("_T")


class Coord:
    __slots__ = ("point",)

    def __init__(self, *args: float | Point):
        self.point = Point(*args)

    def __repr__(self):
        return f"{type(self).__name__} <{repr(self.point)}>"

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.point == other.point
        else:
            return False

    @property
    def x(self) -> float:
        return self.point.x

    @property
    def y(self) -> float:
        return self.point.y

    def as_tuple(self) -> tuple[float, float]:
        return self.point.x, self.point.y

    @staticmethod
    def enc_hook(obj: Coord) -> tuple[int, int]:
        return int(obj.point.x), int(obj.point.y)

    @staticmethod
    def dec_hook(obj: tuple[float, float]) -> Coord:
        return Coord(*obj)

    def __hash__(self):
        return hash((self.x, self.y))


class ImageCoord(Coord):
    def to_world_coord(
        self, skin: Skin, tile_coord: TileCoord, zoom: ZoomParams
    ) -> WorldCoord:
        size = zoom.range * 2 ** (zoom.max - tile_coord[0])
        xc = size / skin.tile_size * self.x
        yc = size / skin.tile_size * self.y
        xs = xc + tile_coord.x * size
        ys = yc + tile_coord.y * size
        return WorldCoord(xs, ys)


class WorldCoord(Coord):
    """Represents a coordinate in the form ``(x, y)``."""

    def to_image_coord(
        self, skin: Skin, tile_coord: TileCoord, zoom: ZoomParams
    ) -> ImageCoord:
        size = zoom.range * 2 ** (zoom.max - tile_coord[0])
        xc = self.x - tile_coord.x * size
        yc = self.y - tile_coord.y * size
        xs = int(skin.tile_size / size * xc)
        ys = int(skin.tile_size / size * yc)
        return ImageCoord(xs, ys)

    def tiles(self, zoom_params: ZoomParams) -> list[TileCoord]:
        # noinspection GrazieInspection
        """
        Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

        :param ZoomParams zoom_params: TODO

        :returns: A list of tile coordinates
        :rtype: List[TileCoord]
        """
        tiles = []
        range_ = zoom_params.range
        for z in reversed(range(zoom_params.min, zoom_params.max + 1)):
            x = math.floor(self.x / range_)
            y = math.floor(self.y / range_)
            tiles.append(TileCoord(z, x, y))
            range_ *= 2

        return tiles


@dataclass
class Bounds(Generic[_T]):
    __slots__ = "x_max", "x_min", "y_max", "y_min"
    x_max: _T
    x_min: _T
    y_max: _T
    y_min: _T


class Line:
    __slots__ = ("line",)

    def __init__(self, line: list[Coord] | LineString):
        if isinstance(line, LineString):
            self.line = line
        else:
            self.line = LineString(p.point for p in line)

    def __repr__(self):
        return f"{type(self).__name__} <{repr(self.line)}>"

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.line == other.line
        else:
            return False

    @property
    def coords(self) -> list[Coord]:
        return [c for c in self]

    def __iter__(self) -> Generator[Coord, Any, None]:
        for c in self.line.coords:
            yield Coord(*c)

    def __len__(self):
        return len(self.line.coords)

    @functools.cached_property
    def bounds(self) -> Bounds[float]:
        """
        Find the minimum and maximum x/y values in a list of coords.

        :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
        :rtype: Tuple[float, float, float, float]"""
        return Bounds(
            x_max=max(c.x for c in self.coords),
            x_min=min(c.x for c in self.coords),
            y_max=max(c.y for c in self.coords),
            y_min=min(c.y for c in self.coords),
        )

    def parallel_offset(self, *args, **kwargs):
        return Line(self.line.parallel_offset(*args, **kwargs))

    @property
    def centroid(self):
        return self.line.centroid

    def to_tiles(self, z: ZoomParams) -> list[TileCoord]:
        """
        Generates tile coordinates from list of regular coordinates using :py:func:`tools.coord.to_tiles()`.
            Mainly for rendering whole components.

        :param ZoomParams z: TODO

        :returns: A list of tile coordinates
        :rtype: List[TileCoord]
        """

        bounds = Bounds(
            x_max=int(max(c.x for c in self.coords)) + 10,
            x_min=int(min(c.x for c in self.coords)) - 10,
            y_max=int(max(c.y for c in self.coords)) + 10,
            y_min=int(min(c.y for c in self.coords)) - 10,
        )
        xr = list(range(bounds.x_min, bounds.x_max + 1, int(z.range / 2)))
        xr.append(bounds.x_max + 1)
        yr = list(range(bounds.y_min, bounds.y_max + 1, int(z.range / 2)))
        yr.append(bounds.y_max + 1)
        tiles = (WorldCoord(x, y).tiles(z) for x in xr for y in yr)
        return list(set(chain(*tiles)))

    def in_bounds(self, bounds: Bounds[int]) -> bool:
        for c1, c2 in with_next([a for a in self]):
            for c3, c4 in (
                (Coord(bounds.y_max, bounds.x_min), Coord(bounds.y_min, bounds.x_min)),
                (Coord(bounds.y_min, bounds.x_min), Coord(bounds.y_min, bounds.x_max)),
                (Coord(bounds.y_min, bounds.x_max), Coord(bounds.y_max, bounds.x_max)),
                (Coord(bounds.y_max, bounds.x_max), Coord(bounds.y_max, bounds.x_min)),
            ):
                if math_utils.segments_intersect(c1, c2, c3, c4):
                    return True
        for c in self:
            if bounds.y_min < c.x < bounds.y_max or bounds.x_min < c.y < bounds.x_max:
                return True
        return False


class WorldLine(Line):
    def to_image_line(
        self, skin: Skin, tile_coord: TileCoord, zoom: ZoomParams
    ) -> ImageLine:
        image_coords = [a.to_image_coord(skin, tile_coord, zoom) for a in self]
        return ImageLine(image_coords)

    @property  # type: ignore
    def coords(self) -> list[WorldCoord]:
        return [c for c in self]

    def __iter__(self) -> Generator[WorldCoord, Any, None]:
        for c in self.line.coords:
            yield WorldCoord(*c)


class ImageLine(Line):
    def to_world_line(
        self, skin: Skin, tile_coord: TileCoord, zoom: ZoomParams
    ) -> ImageLine:
        image_coords = [a.to_world_coord(skin, tile_coord, zoom) for a in self]
        return ImageLine(image_coords)

    @property  # type: ignore
    def coords(self) -> list[ImageCoord]:
        return [c for c in self]

    def __iter__(self) -> Generator[ImageCoord, Any, None]:
        for c in self.line.coords:
            yield ImageCoord(*c)


class TileCoord(NamedTuple):
    """Represents a tile coordinate in the form ``(z, x, y)``."""

    z: int
    x: int
    y: int

    def __str__(self) -> str:
        return f"{self.z}, {self.x}, {self.y}"

    @staticmethod
    def bounds(tile_coords: list[TileCoord]) -> Bounds[int]:
        """
        Find the minimum and maximum x/y values in a set of TileCoords.

        :param List[TileCoord] tile_coords: a list of tile coordinates, provide in a tuple of ``(z,x,y)``

        :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
        :rtype: Tuple[float, float, float, float]
        """

        return Bounds(
            x_max=max(c.x for c in tile_coords),
            x_min=min(c.x for c in tile_coords),
            y_max=max(c.y for c in tile_coords),
            y_min=min(c.y for c in tile_coords),
        )
