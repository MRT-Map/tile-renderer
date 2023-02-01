from __future__ import annotations

import math

import vector

from ._internal import with_next
from .types.coord import Coord, ImageCoord, ImageLine


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


def dash(coords: ImageLine, dash_length: float, gap_length: float) -> list[ImageLine]:
    """
    Takes a list of coordinates and returns a list of lines that make up a dashed line.

    :param list[renderer.types.Vector2D.Vector2D] coords: the coordinates
    :param float dash_length: the length of each dash
    :param float gap_length: the length of the gap between dashes
    :return: a list of pairs of Vector2Ds.
    """
    if dash_length <= 0.0 or gap_length <= 0.0:
        raise ValueError("dash or gap length cannot be <= 0")
    dashes = []
    is_gap = False
    overflow = 0.0
    for c1, c2 in with_next([a for a in coords]):
        pre_dashes = [c1]
        plotted_length = 0.0
        start_as_gap = is_gap
        theta = math.atan2(c2.y - c1.y, c2.x - c1.x)
        dash_dx = dash_length * math.cos(theta)
        dash_dy = dash_length * math.sin(theta)
        gap_dx = gap_length * math.cos(theta)
        gap_dy = gap_length * math.sin(theta)
        if overflow != 0.0:
            if overflow > c1.point.distance(c2.point):
                pre_dashes.append(c2)
                overflow -= c1.point.distance(c2.point)
                plotted_length += c1.point.distance(c2.point)
            else:
                overflow_x = overflow * math.cos(theta)
                overflow_y = overflow * math.sin(theta)
                pre_dashes.append(
                    Coord(pre_dashes[-1].x + overflow_x, pre_dashes[-1].y + overflow_y)
                )
                plotted_length += overflow
                is_gap = False if is_gap else True
                overflow = 0.0
        while overflow == 0.0:
            if is_gap:
                dx = gap_dx
                dy = gap_dy
            else:
                dx = dash_dx
                dy = dash_dy
            if math.hypot(dx, dy) > c1.point.distance(c2.point) - plotted_length:
                overflow = math.hypot(dx, dy) - (
                    c1.point.distance(c2.point) - plotted_length
                )
                pre_dashes.append(c2)
            else:
                pre_dashes.append(Coord(pre_dashes[-1].x + dx, pre_dashes[-1].y + dy))
                plotted_length += gap_length if is_gap else dash_length
                is_gap = False if is_gap else True
        for i, (c3, c4) in enumerate(
            with_next(pre_dashes[(1 if start_as_gap else 0) :])
        ):
            if i % 2 == 0 and c3 != c4:
                dashes.append((c3, c4))

    new_dashes = []
    prev_coord: ImageCoord | None = None
    for c1, c2 in dashes:
        if prev_coord != c1:
            new_dashes.append(ImageLine([c1, c2]))
        else:
            new_dashes[-1] = ImageLine([*new_dashes[-1], c2])
        prev_coord = c2
    return new_dashes


def rotate_around_pivot(coord: Coord, pivot: Coord, theta: float) -> Coord:
    """
    Rotates a set of coordinates about a pivot point.

    :param float coord: the coordinate to be rotated
    :param float pivot: the pivot to be rotated about
    :param float theta: angle to rotate in radians

    :returns: The rotated coordinates, given in ``(x,y)``
    :rtype: renderer.types.coord.Coord
    """
    coord_vec = vector.obj(x=coord.x, y=coord.y)
    pivot_vec = vector.obj(x=pivot.x, y=pivot.y)
    coord_vec -= pivot_vec
    new = coord_vec.rotateZ(theta)
    new += pivot_vec
    return Coord(new.x, new.y)
