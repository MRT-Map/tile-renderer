import math
import blessed

import renderer.internals.internal as internal
from renderer.types import *

term = blessed.Terminal()

def to_tiles(coord: Coord, min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> list[TileCoord]:
    """
    Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

    :param Coord coord: Coordinates provided in the form ``(x,y)``
    :param int min_zoom: minimum zoom value
    :param int max_zoom: maximum zoom value
    :param RealNum max_zoom_range: actual distance covered by a tile in the maximum zoom

    :returns: A list of tile coordinates
    :rtype: List[TileCoord]

    :raises ValueError: if max_zoom < min_zoom
    """
    if max_zoom < min_zoom:
        raise ValueError("Max zoom value is lesser than min zoom value")

    tiles = []
    for z in reversed(range(min_zoom, max_zoom + 1)):
        x = math.floor(coord[0] / max_zoom_range)
        y = math.floor(coord[1] / max_zoom_range)
        tiles.append(TileCoord(z, x, y))
        max_zoom_range *= 2

    return tiles