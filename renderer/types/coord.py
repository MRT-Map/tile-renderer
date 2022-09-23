from __future__ import annotations

import functools
import math
from dataclasses import dataclass
from typing import Generic, NamedTuple, Self, TypeVar

import numpy as np
import vector
from nptyping import Int, NDArray, Shape
from vector import Vector2D

from renderer.internals import internal
from renderer.types.zoom_params import ZoomParams

_T = TypeVar("_T")


class ImageCoord(Vector2D):
    pass


class WorldCoord(Vector2D):
    """Represents a coordinate in the form ``(x, y)``."""

    def __new__(cls, x: int, y: int, **kwargs):
        return vector.arr(x, y)

    def tiles(self, z: ZoomParams) -> list[TileCoord]:
        # noinspection GrazieInspection
        """
        Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

        :param renderer.types.coord.WorldCoord coord: Coordinates provided in the form ``(x,y)``

        :returns: A list of tile coordinates
        :rtype: List[TileCoord]
        """
        tiles = []
        range_ = z.range
        for z in reversed(range(z.min, z.max + 1)):
            x = math.floor(self.x / range_)
            y = math.floor(self.y / range_)
            tiles.append(TileCoord(z, x, y))
            range_ *= 2

        return tiles


@dataclass
class Bounds(Generic[_T]):
    x_max: _T
    x_min: _T
    y_max: _T
    y_min: _T


class WorldLine:
    coords: list[WorldCoord]

    @classmethod
    def validate(cls, v: list[tuple[int, int]]) -> Self:
        c = cls()
        c.coords = [vector.arr(x, y) for x, y in v]
        return c

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @functools.cached_property
    def np(self) -> NDArray[Shape["*, 2"], Int]:
        return np.array(self.coords)

    def __iter__(self):
        for c in self.coords:
            yield c

    @functools.cached_property
    def bounds(self) -> Bounds[int]:
        """
        Find the minimum and maximum x/y values of a set of coords.

        :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
        :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]"""
        return Bounds(
            x_max=max(c.x for c in self.coords),
            x_min=min(c.x for c in self.coords),
            y_max=max(c.y for c in self.coords),
            y_min=min(c.y for c in self.coords),
        )

    def to_tiles(self, z: ZoomParams) -> list[TileCoord]:
        """
        Generates tile coordinates from list of regular coordinates using :py:func:`tools.coord.to_tiles()`. Mainly for rendering whole components.

        :param List[WorldCoord] coords: of coordinates in tuples of ``(x,y)``
        :param int min_zoom: minimum zoom value
        :param int max_zoom: maximum zoom value
        :param RealNum max_zoom_range: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``max_zoom`` of 5 and a ``max_zoomValue`` of 8 will make a 5-zoom tile cover 8 units

        :returns: A list of tile coordinates
        :rtype: List[TileCoord]
        """

        bounds = Bounds(
            x_max=max(c.x for c in self.coords) + 10,
            x_min=min(c.x for c in self.coords) - 10,
            y_max=max(c.y for c in self.coords) + 10,
            y_min=min(c.y for c in self.coords) - 10,
        )
        xr = list(range(bounds.x_min, bounds.x_max + 1, int(z.range / 2)))
        xr.append(bounds.x_max + 1)
        yr = list(range(bounds.y_min, bounds.y_max + 1, int(z.range / 2)))
        yr.append(bounds.y_max + 1)
        tiles = [WorldCoord(x, y).tiles(z) for x in xr for y in yr]
        tiles = list(set(*tiles))
        return tiles


class TileCoord(NamedTuple):
    """Represents a tile coordinate in the form ``(z, x, y)``."""

    z: int
    x: int
    y: int

    def __str__(self) -> str:
        return internal._tuple_to_str((self.z, self.x, self.y))

    @staticmethod
    def bounds(tile_coords: list[TileCoord]) -> Bounds[int]:
        """
        Find the minimum and maximum x/y values of a set of TileCoords.

        :param List[TileCoord] coords: a list of tile coordinates, provide in a tuple of ``(z,x,y)``

        :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
        :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
        """

        return Bounds(
            x_max=max(c.x for c in tile_coords),
            x_min=min(c.x for c in tile_coords),
            y_max=max(c.y for c in tile_coords),
            y_min=min(c.y for c in tile_coords),
        )
