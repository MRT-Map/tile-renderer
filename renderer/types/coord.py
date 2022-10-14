from __future__ import annotations

import functools
import math
from dataclasses import dataclass
from typing import Any, Generator, Generic, NamedTuple, TypeVar, TYPE_CHECKING

import numpy as np
from nptyping import Int, NDArray, Shape
from shapely.geometry import LineString, Point

from renderer import math_utils
from renderer.internals import internal
if TYPE_CHECKING:
    from renderer.types.skin import Skin
from renderer.types.zoom_params import ZoomParams

_T = TypeVar("_T")


class Coord(Point):
    pass


class ImageCoord(Coord):
    pass


class WorldCoord(Coord):
    """Represents a coordinate in the form ``(x, y)``."""

    def tiles(self, z: ZoomParams) -> list[TileCoord]:
        # noinspection GrazieInspection
        """
        Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

        :param ZoomParams z: TODO

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


class Line(LineString):
    @functools.cached_property
    def np(self) -> NDArray[Shape["*, 2"], Int]:
        return np.array(self.coords)

    def __iter__(self) -> Generator[WorldCoord, Any, None]:
        for c in self.coords:
            yield WorldCoord(c)

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

        :param ZoomParams z: TODO

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

    def in_bounds(self, bounds: Bounds[int]) -> bool:
        for c1, c2 in internal._with_next(a for a in self):
            for c3, c4 in [
                (Coord(bounds.y_max, bounds.x_min), Coord(bounds.y_min, bounds.x_min)),
                (Coord(bounds.y_min, bounds.x_min), Coord(bounds.y_min, bounds.x_max)),
                (Coord(bounds.y_min, bounds.x_max), Coord(bounds.y_max, bounds.x_max)),
                (Coord(bounds.y_max, bounds.x_max), Coord(bounds.y_max, bounds.x_min)),
            ]:
                if math_utils.segments_intersect(c1, c2, c3, c4):
                    return True
        for c in self:
            if bounds.y_min < c.x < bounds.y_max or bounds.x_min < c.y < bounds.x_max:
                return True
        return False


class WorldLine(Line):
    def to_image_line(
        self, skin: Skin, tile_coord: TileCoord, size: float | int
    ) -> ImageLine:
        image_coords = []
        for coord in self:
            xc = coord.x - tile_coord.x * size
            yc = coord.y - tile_coord.y * size
            xs = int(skin.tile_size / size * xc)
            ys = int(skin.tile_size / size * yc)
            image_coords.append(ImageCoord(xs, ys))
        return ImageLine(image_coords)


class ImageLine(Line):
    pass


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

        :param List[TileCoord] tile_coords: a list of tile coordinates, provide in a tuple of ``(z,x,y)``

        :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
        :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
        """

        return Bounds(
            x_max=max(c.x for c in tile_coords),
            x_min=min(c.x for c in tile_coords),
            y_max=max(c.y for c in tile_coords),
            y_min=min(c.y for c in tile_coords),
        )
