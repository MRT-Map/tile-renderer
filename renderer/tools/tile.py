import math
from typing import Tuple

import blessed

import renderer.internals.internal as internal # type: ignore
import renderer.validate as validate
from renderer.types import *

term = blessed.Terminal()

def find_ends(coords: list[TileCoord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
    """
    Find the minimum and maximum x/y values of a set of TileCoords.

    :param List[TileCoord] coords: a list of tile coordinates, provide in a tuple of ``(z,x,y)``

    :returns: Returns in the form ``(x_max, x_min, y_max, y_min)``
    :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
    """
    validate.v_tile_coords(coords, -math.inf, math.inf)
    x_max = -math.inf
    x_min = math.inf
    y_max = -math.inf
    y_min = math.inf
    for _, x, y in coords:
        x_max = x if x > x_max else x_max
        x_min = x if x < x_min else x_min
        y_max = y if y > y_max else y_max
        y_min = y if y < y_min else y_min
    return x_max, x_min, y_max, y_min