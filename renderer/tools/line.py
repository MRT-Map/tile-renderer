import math
from typing import Tuple

import blessed

import renderer.validate as validate
import renderer.tools.coord as tools_coord
from renderer.types import *

term = blessed.Terminal()

def find_ends(coords: list[Coord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
    """
    Find the minimum and maximum x/y values of a set of coords.

    :param List[Coord] coords: a list of coordinates, provide in a tuple of ``(x,y)``

    :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
    :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]"""
    validate.v_coords(coords)
    x_max = -math.inf
    x_min = math.inf
    y_max = -math.inf
    y_min = math.inf
    for x, y in coords:
        x_max = x if x > x_max else x_max
        x_min = x if x < x_min else x_min
        y_max = y if y > y_max else y_max
        y_min = y if y < y_min else y_min
    return x_max, x_min, y_max, y_min

def to_tiles(coords: list[Coord], min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> list[TileCoord]:
    """
    Generates tile coordinates from list of regular coordinates using :py:func:`tools.coord.to_tiles()`. Mainly for rendering whole components.

    :param List[Coord] coords: of coordinates in tuples of ``(x,y)``
    :param int min_zoom: minimum zoom value
    :param int max_zoom: maximum zoom value
    :param RealNum max_zoom_range: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``max_zoom`` of 5 and a ``max_zoomValue`` of 8 will make a 5-zoom tile cover 8 units

    :returns: A list of tile coordinates
    :rtype: List[TileCoord]

    :raises ValueError: if max_zoom < min_zoom
    :raises ValueError: if empty list of coords given
    """
    validate.v_coords(coords)
    if len(coords) == 0:
        raise ValueError("Empty list of coords given")
    elif max_zoom < min_zoom:
        raise ValueError("Max zoom value is lesser than min zoom value")

    tiles = []
    x_max = -math.inf
    x_min = math.inf
    y_max = -math.inf
    y_min = math.inf

    for x, y in coords:
        x_max = x + 10 if x > x_max else x_max
        x_min = x - 10 if x < x_min else x_min
        y_max = y + 10 if y > y_max else y_max
        y_min = y - 10 if y < y_min else y_min
    xr = list(range(x_min, x_max + 1, int(max_zoom_range / 2)))
    xr.append(x_max + 1)
    yr = list(range(y_min, y_max + 1, int(max_zoom_range / 2)))
    yr.append(y_max + 1)
    for x in xr:
        for y in yr:
            tiles.extend(tools_coord.to_tiles(Coord(x, y), min_zoom, max_zoom, max_zoom_range))
    tiles = list(dict.fromkeys(tiles))
    return tiles