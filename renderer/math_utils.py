from __future__ import annotations

import math
from itertools import product

import numpy as np
import vector

from renderer.internals import internal
from renderer.types import *
from renderer.types.coord import Coord, Line, ImageLine


def segments_intersect(c1: Coord, c2: Coord, c3: Coord, c4: Coord) -> bool:
    """
    Finds if two segments intersect.

    :param Coord c1: the 1st point of the 1st segment.
    :param Coord c2: the 2nd point of the 1st segment.
    :param Coord c3: the 1st point of the 2nd segment.
    :param Coord c4: the 2nd point of the 2nd segment.

    :returns: Whether the two segments intersect.
    :rtype: bool
    """
    # https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines lol
    xdiff = Coord(c1.x - c2.x, c3.x - c4.x)
    ydiff = Coord(c1.y - c2.y, c3.y - c4.y)

    def det(a, b):
        return a.x * b.y - a.y * b.x

    div = det(xdiff, ydiff)
    if div == 0:
        return False
    d = Coord(det(c1, c2), det(c3, c4))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (
        min(c1.x, c2.x) <= x <= max(c1.x, c2.x)
        and min(c1.y, c2.y) <= y <= max(c1.y, c2.y)
        and min(c3.x, c4.x) <= x <= max(c3.x, c4.x)
        and min(c3.y, c4.y) <= y <= max(c3.y, c4.y)
    )


def point_in_poly(xp: RealNum, yp: RealNum, line: Line) -> bool:
    """
    Finds if a point is in a polygon.

    :param RealNum xp: the x-coordinate of the point.
    :param RealNum yp: the y-coordinate of the point.
    :param list[renderer.types.Vector2D.Vector2D] line: the coordinates of the polygon; give in ``(x,y)``

    :returns: Whether the point is inside the polygon.
    :rtype: bool
    """
    if Coord(xp, yp) in line.coords:
        return True
    coords = np.asarray(line)
    xs = coords[:, 0] - xp
    ys = coords[:, 1] - yp
    bearings = np.diff(np.arctan2(ys, xs))
    bearings = np.where(bearings >= -math.pi, bearings, bearings + math.tau)
    bearings = np.where(bearings <= math.pi, bearings, bearings - math.tau)
    wind_num = round(bearings.sum() / math.tau)
    return wind_num != 0


def poly_intersect(poly1: Line, poly2: Line) -> bool:
    coords1 = [i for i in internal._with_next(poly1)]
    coords2 = [i for i in internal._with_next(poly2)]
    for (c1, c2), (c3, c4) in product(coords1, coords2):
        if segments_intersect(c1, c2, c3, c4):
            return True
    if all(point_in_poly(x, y, poly2) for x, y in poly1):
        return True
    if all(point_in_poly(x, y, poly1) for x, y in poly2):
        return True
    return False


def dash(coords: ImageLine, dash_length: RealNum, gap_length: RealNum) -> list[ImageLine]:
    """
    Takes a list of coordinates and returns a list of lines.

    :param list[renderer.types.Vector2D.Vector2D] coords: the coordinates
    :param RealNum dash_length: the length of each dash
    :param RealNum gap_length:RealNum: the length of the gap between dashes
    :return: a list of pairs of Vector2Ds.
    """
    if dash_length <= 0 or gap_length <= 0:
        raise ValueError("dash or gap length cannot be <= 0")
    dashes = []
    is_gap = False
    overflow = 0
    for c1, c2 in internal._with_next(a for a in coords):
        predashes = [c1]
        plotted_length = 0
        start_as_gap = is_gap
        theta = math.atan2(c2.y - c1.y, c2.x - c1.x)
        dash_dx = dash_length * math.cos(theta)
        dash_dy = dash_length * math.sin(theta)
        gap_dx = gap_length * math.cos(theta)
        gap_dy = gap_length * math.sin(theta)
        if overflow != 0:
            if overflow > c1.distance(c2):
                predashes.append(c2)
                overflow -= c1.distance(c2)
                plotted_length += c1.distance(c2)
            else:
                overflow_x = overflow * math.cos(theta)
                overflow_y = overflow * math.sin(theta)
                predashes.append(
                    Coord(predashes[-1].x + overflow_x, predashes[-1].y + overflow_y)
                )
                plotted_length += overflow
                is_gap = False if is_gap else True
                overflow = 0
        while overflow == 0:
            if is_gap:
                dx = gap_dx
                dy = gap_dy
            else:
                dx = dash_dx
                dy = dash_dy
            if (dx**2 + dy**2) ** 0.5 > c1.distance(c2) - plotted_length:
                overflow = (dx**2 + dy**2) ** 0.5 - (
                    c1.distance(c2) - plotted_length
                )
                predashes.append(c2)
            else:
                predashes.append(Coord(predashes[-1].x + dx, predashes[-1].y + dy))
                plotted_length += gap_length if is_gap else dash_length
                is_gap = False if is_gap else True
        for i, (c3, c4) in enumerate(
            internal._with_next(predashes[(1 if start_as_gap else 0) :])
        ):
            if i % 2 == 0 and c3 != c4:
                dashes.append((c3, c4))

    new_dashes = []
    prev_coord = None
    for c1, c2 in dashes:
        if prev_coord != c1:
            new_dashes.append(Line([c1, c2]))
        else:
            new_dashes[-1] = Line([*new_dashes[-1], c2])
        prev_coord = c2
    return new_dashes


def rotate_around_pivot(coord: Coord, pivot: Coord, theta: float) -> Coord:
    """
    Rotates a set of Vector2Dinates around a pivot point.

    :param RealNum x: the x-Vector2Dinate to be rotated
    :param RealNum y: the y-Vector2Dinate to be rotated
    :param RealNum px: the x-Vector2Dinate of the pivot
    :param RealNum py: the y-Vector2Dinate of the pivot
    :param RealNum theta: how many **radians** to rotate

    :returns: The rotated coordinates, given in ``(x,y)``
    :rtype: renderer.types.Vector2D.Vector2D
    """
    coord = vector.obj(x=coord.x, y=coord.y)
    pivot = vector.obj(x=pivot.x, y=pivot.y)
    coord -= pivot
    new = coord.rotateZ(theta)
    new += pivot
    return Coord(new.x, new.y)
