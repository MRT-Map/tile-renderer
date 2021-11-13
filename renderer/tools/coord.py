import math
import blessed

import renderer.internals.internal as internal
from renderer.types import *

term = blessed.Terminal()

def to_tiles(coord: Coord, min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> List[TileCoord]:
    """
    Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.coord.toTiles
    """
    if max_zoom < min_zoom:
        raise ValueError("Max zoom value is lesser than min zoom value")

    tiles = []
    for z in reversed(range(min_zoom, max_zoom + 1)):
        x = math.floor(coord[0] / max_zoom_range)
        y = math.floor(coord[1] / max_zoom_range)
        tiles.append((z, x, y))
        max_zoom_range *= 2

    return tiles