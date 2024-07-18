from __future__ import annotations

import dataclasses
import functools
from copy import copy
from typing import TYPE_CHECKING, Self

from shapely import LinearRing, LineString, Point

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclasses.dataclass
class Vector[T: float | int]:
    """Represents a 2-dimensional vector"""

    x: T
    y: T

    def __repr__(self) -> str:
        return f"[{self.x}, {self.y}]"

    def as_tuple(self) -> tuple[T, T]:
        """Represent the coordinates as a tuple"""
        return self.x, self.y

    def to_float(self) -> Vector[float]:
        return Vector(float(self.x), float(self.y))

    def to_int(self) -> Vector[int]:
        return Vector(round(self.x), round(self.y))

    def __add__(self, other: T | Self) -> Self:
        s = copy(self)
        if isinstance(other, Vector):
            s.x += other.x
            s.y += other.y
        else:
            s.x += other
            s.y += other
        return s

    def __sub__(self, other: T | Self) -> Self:
        s = copy(self)
        if isinstance(other, Vector):
            s.x -= other.x
            s.y -= other.y
        else:
            s.x -= other
            s.y -= other
        return s

    def __mul__(self, other: T) -> Self:
        s = copy(self)
        s.x *= other
        s.y *= other
        return s

    def __truediv__(self, other: T) -> Self:
        s = copy(self)
        s.x /= other
        s.y /= other
        return s

    def __abs__(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def unit(self) -> Vector[float]:
        """Normalises the vector"""
        return self / abs(self)

    def dot(self, other: Self) -> T:
        """Dot product"""
        return self.x * other.x + self.y * other.y

    def encode(self) -> tuple[T, T]:
        """Encoding hook for msgspec"""
        return self.x, self.y

    @classmethod
    def decode(cls, obj: tuple[T, T]) -> Self:
        """Decoding hook for msgspec"""
        return cls(*obj)


@dataclasses.dataclass
class Coord[T: float | int](Vector[T]):
    """Represents a 2-dimensional point"""

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y})"

    def to_float(self) -> Coord[float]:
        return Coord(float(self.x), float(self.y))

    def to_int(self) -> Coord[int]:
        return Coord(round(self.x), round(self.y))

    @property
    def point(self) -> Point:
        """Returns a Shapely point"""
        return Point(self.x, self.y)


@dataclasses.dataclass
class Bounds[T: float | int]:
    """Represents a bounding box, like a rectangle"""

    x_max: T
    x_min: T
    y_max: T
    y_min: T


@dataclasses.dataclass
class Line[T: float | int]:
    """Represents a 2-dimensional line"""

    coords: list[Coord[T]]

    def __repr__(self) -> str:
        return f"{type(self).__name__} <{''.join(str(a.as_tuple()) for a in self.coords)}>"

    def __getitem__(self, item: int) -> Coord[T]:
        return self.coords[item]

    def __iter__(self) -> Iterator[Coord[T]]:
        yield from self.coords

    def __len__(self) -> int:
        return len(self.coords)

    def to_float(self) -> Line[float]:
        return Line([c.to_float() for c in self.coords])

    def to_int(self) -> Line[int]:
        return Line([c.to_int() for c in self.coords])

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

    def parallel_offset(self, distance: float) -> Line[float]:
        """Calculates a line that is the parallel offset of this line"""
        if distance == 0:
            return self
        return Line(
            [Coord(*a) for a in LineString(a.as_tuple() for a in self.coords).offset_curve(distance).coords],
        )

    @property
    def centroid(self) -> Coord[float]:
        """Finds the visual center"""
        coords = [c - self.coords[0] for c in self.coords]
        centroid = LinearRing({a.as_tuple() for a in coords}).centroid
        return Coord(centroid.x + self.coords[0].x, centroid.y + self.coords[0].y)

    def encode(self) -> list[tuple[T, T]]:
        """Encoding hook for msgspec"""
        return [c.encode() for c in self.coords]

    @classmethod
    def decode(cls, obj: list[tuple[T, T]]) -> Self:
        """Decoding hook for msgspec"""
        return cls([Coord.decode(c) for c in obj])


@dataclasses.dataclass
class TileCoord:
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