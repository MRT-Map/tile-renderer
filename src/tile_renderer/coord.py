from __future__ import annotations

import dataclasses
import functools
from typing import TYPE_CHECKING, Self, cast, overload

from shapely import LineString, MultiLineString, Point, Polygon
from shapely import ops
from shapely.ops import substring

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclasses.dataclass
class Vector[T: float | int]:
    x: T
    y: T

    def __repr__(self) -> str:
        return f"[{self.x}, {self.y}]"

    def as_tuple(self) -> tuple[T, T]:
        return self.x, self.y

    def to_float(self) -> Vector[float]:
        return Vector(float(self.x), float(self.y))

    def to_int(self) -> Vector[int]:
        return Vector(round(self.x), round(self.y))

    @overload
    def __add__(self: Vector[int], other: Vector[int]) -> Vector[int]:
        pass

    @overload
    def __add__(self: Vector[float], other: Vector[int] | Vector[float]) -> Vector[float]:
        pass

    @overload
    def __add__(self: Vector[int], other: int) -> Vector[int]:
        pass

    @overload
    def __add__(self: Vector[float], other: float) -> Vector[float]:
        pass

    def __add__(self, other):
        if isinstance(other, Vector):
            return cast(type, type(self))(self.x + other.x, self.y + other.y)
        return Vector(self.x + other, self.y + other)

    @overload
    def __sub__(self: Vector[int], other: Vector[int]) -> Vector[int]:
        pass

    @overload
    def __sub__(self: Vector[float], other: Vector[int] | Vector[float]) -> Vector[float]:
        pass

    @overload
    def __sub__(self: Vector[int], other: int) -> Vector[int]:
        pass

    @overload
    def __sub__(self: Vector[float], other: float) -> Vector[float]:
        pass

    def __sub__(self, other):
        if isinstance(other, Vector):
            return cast(type, type(self))(self.x - other.x, self.y - other.y)
        return Vector(self.x - other, self.y - other)

    @overload
    def __mul__(self: Vector[int], other: int) -> Vector[int]:
        pass

    @overload
    def __mul__(self: Vector[float], other: float) -> Vector[float]:
        pass

    def __mul__(self, other):
        return cast(type, type(self))(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> Vector[float]:
        return cast(type, type(self))(self.x / other, self.y / other)

    def __abs__(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def __neg__(self) -> Self:
        return cast(type, type(self))(-self.x, -self.y)

    def unit(self) -> Vector[float]:
        return self / abs(self)

    @overload
    def dot(self: Vector[int], other: Vector[int]) -> int:
        pass

    @overload
    def dot(self: Vector[float], other: Vector[int] | Vector[float]) -> float:
        pass

    @overload
    def dot(self: Vector[int], other: Vector[float]) -> float:
        pass

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def perp(self) -> Self:
        return cast(type, type(self))(-self.y, self.x)

    def encode(self) -> tuple[T, T]:
        return self.x, self.y

    @classmethod
    def decode(cls, obj: tuple[T, T]) -> Self:
        return cls(*obj)


@dataclasses.dataclass
class Coord[T: float | int](Vector[T]):
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y})"

    def to_float(self) -> Coord[float]:
        return Coord(float(self.x), float(self.y))

    def to_int(self) -> Coord[int]:
        return Coord(round(self.x), round(self.y))

    @property
    def shapely(self) -> Point:
        return Point(self.x, self.y)


ORIGIN: Coord = Coord(0, 0)


@dataclasses.dataclass(frozen=True)
class Bounds[T: float | int]:
    x_max: T
    x_min: T
    y_max: T
    y_min: T

    @overload
    def __add__(self: Bounds[int], other: Bounds[int]) -> Bounds[int]:
        pass

    @overload
    def __add__(self: Bounds[int], other: Bounds[float]) -> Bounds[float]:
        pass

    @overload
    def __add__(self: Bounds[float], other: Bounds[int] | Bounds[float]) -> Bounds[float]:
        pass

    def __add__(self, other):
        return Bounds(
            x_max=max(self.x_max, other.x_max),
            x_min=min(self.x_min, other.x_min),
            y_max=max(self.y_max, other.y_max),
            y_min=min(self.y_min, other.y_min),
        )


@dataclasses.dataclass(frozen=True)
class Line[T: float | int]:
    coords: list[Coord[T]]

    def __repr__(self) -> str:
        return f"{type(self).__name__} <{''.join(str(a.as_tuple()) for a in self.coords)}>"

    @overload
    def __getitem__(self, item: int) -> Coord[T]:
        pass

    @overload
    def __getitem__(self, item: slice) -> list[Coord[T]]:
        pass

    def __getitem__(self, item):
        return self.coords[item]

    def __iter__(self) -> Iterator[Coord[T]]:
        yield from self.coords

    def __len__(self) -> int:
        return len(self.coords)

    def __contains__(self, item: Coord[T]):
        return item in self.coords

    def to_float(self) -> Line[float]:
        return Line([c.to_float() for c in self.coords])

    def to_int(self) -> Line[int]:
        return Line([c.to_int() for c in self.coords])

    @property
    def shapely(self) -> LineString:
        return LineString(a.as_tuple() for a in self.coords)

    @property
    def shapely_poly(self) -> Polygon | None:
        coords = self.coords if self.coords[0] == self.coords[-1] else [*self.coords, self.coords[0]]
        try:
            return Polygon(a.as_tuple() for a in coords)
        except ValueError as e:
            if "A linearring requires at least 4 coordinates." in str(e):
                return None
            raise

    @functools.cached_property
    def bounds(self) -> Bounds[float]:
        return Bounds(
            x_max=max(c.x for c in self.coords),
            x_min=min(c.x for c in self.coords),
            y_max=max(c.y for c in self.coords),
            y_min=min(c.y for c in self.coords),
        )

    def parallel_offset(self, distance: float) -> Self | Line[float]:
        if distance == 0:
            return self
        line = self.shapely.offset_curve(distance)
        if isinstance(line, MultiLineString):
            line = ops.linemerge(line)
        return Line(
            [Coord(*a) for a in line.coords],
        )

    @property
    def point_on_surface(self) -> Coord[float]:
        point = self.shapely.centroid
        if (poly := self.shapely_poly) is not None and not poly.contains(point):
            point = self.shapely.point_on_surface()
        return Coord(point.x, point.y)

    def dash(self, dash_length: float, shift: bool = False) -> list[Line[float]] | None:  # noqa: FBT001 FBT002
        if dash_length == 0:
            return None
        coords = self.shapely
        out = []
        dist = (coords.length % dash_length) / 2 - (dash_length if shift else 0)
        while dist < coords.length - dash_length:
            dash = Line(
                [Coord(*c) for c in substring(coords, start_dist=max(dist, 0), end_dist=dist + dash_length).coords]
            )
            if len(dash) != 1:
                out.append(dash)
            dist += dash_length * 2
        return out

    def encode(self) -> list[tuple[T, T]]:
        return [c.encode() for c in self.coords]

    @classmethod
    def decode(cls, obj: list[tuple[T, T]]) -> Self:
        return cls([Coord.decode(c) for c in obj])


@dataclasses.dataclass(frozen=True)
class TileCoord:
    z: int

    x: int

    y: int

    def __str__(self) -> str:
        return f"{self.z}, {self.x}, {self.y}"

    def bounds(self, max_zoom_range: int) -> Bounds[int]:
        zoom_range = max_zoom_range * 2**self.z
        return Bounds(
            x_max=(self.x + 1) * zoom_range,
            x_min=self.x * zoom_range,
            y_max=(self.y + 1) * zoom_range,
            y_min=self.y * zoom_range,
        )
