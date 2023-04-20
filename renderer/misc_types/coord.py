from __future__ import annotations

import functools
import math
from copy import copy
from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

import methodtools
from shapely import LinearRing
from shapely.geometry import LineString, Point

from .._internal import with_next

if TYPE_CHECKING:
    from collections.abc import Generator

    from typing_extensions import Self

    from .config import Config
    from .zoom_params import ZoomParams

_T = TypeVar("_T")


@dataclass(init=True, unsafe_hash=True, slots=True, eq=True)
class Vector:
    """Represents a 2-dimensional vector"""

    _x: float
    _y: float

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __repr__(self) -> str:
        return f"[{self.x}, {self.y}]"

    def as_tuple(self) -> tuple[float, float]:
        """Represent the coordinates as a tuple"""
        return self.x, self.y

    def __add__(self, other: float | int | Vector) -> Self:
        s = copy(self)
        if isinstance(other, Vector):
            s._x += other._x
            s._y += other._y
        else:
            s._x += other
            s._y += other
        return s

    def __sub__(self, other: float | int | Vector) -> Self:
        s = copy(self)
        if isinstance(other, Vector):
            s._x -= other._x
            s._y -= other._y
        else:
            s._x -= other
            s._y -= other
        return s

    def __mul__(self, other: float | int) -> Self:
        s = copy(self)
        s._x *= other
        s._y *= other
        return s

    def __truediv__(self, other: float | int) -> Self:
        s = copy(self)
        s._x /= other
        s._y /= other
        return s

    def __abs__(self) -> float:
        return (self._x**2 + self._y**2) ** 0.5

    def unit(self) -> Self:
        """Normalises the vector"""
        return self / abs(self)

    def dot(self, other: Vector) -> float:
        """Dot product"""
        return self._x * other._x + self._y * other._y


class Coord(Vector):
    """Represents a 2-dimensional point"""

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y})"

    @property
    def point(self) -> Point:
        """Returns a Shapely point"""
        return Point(self.x, self.y)

    @staticmethod
    def enc_hook(obj: Coord) -> tuple[int, int]:
        """Encoding hook for msgspec"""
        return int(obj.x), int(obj.y)

    @staticmethod
    def dec_hook(obj: tuple[float, float]) -> Coord:
        """Decoding hook for msgspec"""
        return Coord(*obj)


class ImageCoord(Coord):
    """Represents a 2-dimensional coordinate on an image"""

    @property
    def x(self) -> int:
        return int(self._x)

    @property
    def y(self) -> int:
        return int(self._y)

    def to_world_coord(
        self,
        tile_coord: TileCoord,
        config: Config,
    ) -> WorldCoord:
        """
        Converts the coordinate to a WorldCoord

        :param tile_coord: The tile coordinate that the coordinate is part of
        :param config: The configuration
        """
        size = config.zoom.range * 2 ** (config.zoom.max - tile_coord.z)
        xc = size / config.skin.tile_size * self._x
        yc = size / config.skin.tile_size * self._y
        xs = xc + tile_coord.x * size
        ys = yc + tile_coord.y * size
        return WorldCoord(xs, ys)


@functools.cache
def _to_image_coord(
    wc: WorldCoord,
    tc: TileCoord,
    tile_size: int,
    zoom: ZoomParams,
) -> ImageCoord:
    size = zoom.range * 2 ** (zoom.max - tc.z)
    xc = wc.x - tc.x * size
    yc = wc.y - tc.y * size
    xs = tile_size / size * xc
    ys = tile_size / size * yc
    return ImageCoord(xs, ys)


class WorldCoord(Coord):
    """Represents a 2-dimensional coordinate in the world"""

    def to_image_coord(self, tile_coord: TileCoord, config: Config) -> ImageCoord:
        """
        Converts the coordinate to an ImageCoord

        :param tile_coord: The tile coordinate that the coordinate is part of
        :param config: The configuration
        """

        return _to_image_coord(self, tile_coord, config.skin.tile_size, config.zoom)

    def tiles(self, zoom_params: ZoomParams) -> list[TileCoord]:
        """
        Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.
        """
        tiles = []
        range_ = zoom_params.range
        for z in reversed(range(zoom_params.min, zoom_params.max + 1)):
            x = math.floor(self.x / range_)
            y = math.floor(self.y / range_)
            tiles.append(TileCoord(z, x, y))
            range_ *= 2

        return tiles


def _centroid(coords: list[Coord]) -> Point:
    return LinearRing({a.as_tuple() for a in coords}).centroid


@dataclass
class Bounds(Generic[_T]):
    """Represents a bounding box, like a rectangle"""

    __slots__ = "x_max", "x_min", "y_max", "y_min"
    x_max: _T
    x_min: _T
    y_max: _T
    y_min: _T


class Line:
    """Represents a 2-dimensional line"""

    coords: list[Coord]

    __slots__ = ("coords",)

    def __init__(self, coords: list[Coord]) -> None:
        self.coords = coords

    def __repr__(self) -> str:
        return f"{type(self).__name__} <{';'.join(str(a) for a in self.coords)}>"

    def __getitem__(self, item: int) -> Coord:
        return self.coords[item]

    @methodtools.lru_cache
    def __iter__(self) -> Generator[Coord, Any, None]:
        yield from self.coords

    def __len__(self) -> int:
        return len(self.coords)

    @functools.cached_property
    def bounds(self) -> Bounds[float]:
        """
        Find the minimum and maximum x/y values in a list of coords.
        """
        return Bounds(
            x_max=max(c.x for c in self.coords),
            x_min=min(c.x for c in self.coords),
            y_max=max(c.y for c in self.coords),
            y_min=min(c.y for c in self.coords),
        )

    def parallel_offset(self, distance: float) -> Line:
        """Calculates a line that is the parallel offset of this line"""
        if distance == 0:
            return self
        """Calls shapely.LineString.parallel_offset()"""
        return Line(
            [
                Coord(*a)
                for a in LineString(a.as_tuple() for a in self.coords)
                .offset_curve(distance)
                .coords
            ],
        )

    @property
    def centroid(self) -> Coord:
        """Finds the visual center"""
        coords = [c - self.coords[0] for c in self.coords]
        centroid = _centroid(coords)
        return Coord(centroid.x + self.coords[0].x, centroid.y + self.coords[0].y)

    def to_tiles(self, z: ZoomParams) -> list[TileCoord]:
        """
        Generates tile coordinates from a list of regular coordinates.
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
        """
        Finds whether any part of the LineString is entirely within a bound
        """
        from .. import math_utils

        for c1, c2 in with_next(list(self)):
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

    def __hash__(self) -> int:
        return hash(self.coords)


class WorldLine(Line):
    """Represents a line in the world"""

    coords: list[WorldCoord]

    def __init__(self, line: list[WorldCoord] | LineString) -> None:
        super().__init__(line)

    def __getitem__(self, item: int) -> WorldCoord:
        return self.coords[item]

    def to_image_line(self, tile_coord: TileCoord, config: Config) -> ImageLine:
        """
        Converts the line into an ImageLine

        :param tile_coord: The tile coordinate that the coordinate is part of
        :param config: The configuration
        """
        image_coords = [a.to_image_coord(tile_coord, config) for a in self]
        return ImageLine(image_coords)

    def __iter__(self) -> Generator[WorldCoord, Any, None]:
        yield from self.coords

    def parallel_offset(self, distance: float) -> WorldLine:
        if distance == 0:
            return self
        return WorldLine(
            [
                WorldCoord(*a)
                for a in LineString(a.as_tuple() for a in self.coords)
                .offset_curve(distance)
                .coords
            ],
        )


class ImageLine(Line):
    coords: list[ImageCoord]

    def __init__(self, line: list[ImageCoord] | LineString) -> None:
        super().__init__(line)

    def __getitem__(self, item: int) -> ImageCoord:
        return self.coords[item]

    def to_world_line(self, tile_coord: TileCoord, config: Config) -> WorldLine:
        """
        Converts the line into a WorldLine

        :param tile_coord: The tile coordinate that the coordinate is part of
        :param config: The configuration
        """
        image_coords = [a.to_world_coord(tile_coord, config) for a in self]
        return WorldLine(image_coords)

    def __iter__(self) -> Generator[ImageCoord, Any, None]:
        yield from self.coords

    def parallel_offset(self, distance: float) -> ImageLine:
        if distance == 0:
            return self
        return ImageLine(
            [
                ImageCoord(*a)
                for a in LineString(a.as_tuple() for a in self.coords)
                .offset_curve(distance)
                .coords
            ],
        )


class TileCoord(NamedTuple):
    """Represents a tile coordinate in the form ``(z, x, y)``."""

    z: int
    """Represents zoom"""
    x: int
    """Represents x-coordinate"""
    y: int
    """Represents y-coordinate"""

    def __str__(self) -> str:
        return f"{self.z}, {self.x}, {self.y}"

    @staticmethod
    def bounds(tile_coords: list[TileCoord]) -> Bounds[int]:
        """
        Find the minimum and maximum x/y values in a set of TileCoords.
        """

        return Bounds(
            x_max=max(c.x for c in tile_coords),
            x_min=min(c.x for c in tile_coords),
            y_max=max(c.y for c in tile_coords),
            y_min=min(c.y for c in tile_coords),
        )

    def __hash__(self) -> int:
        return hash((self.z, self.x, self.y))
