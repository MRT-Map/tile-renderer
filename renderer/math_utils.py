from __future__ import annotations

import functools

import vector

from ._internal import with_next
from .misc_types.coord import Coord, ImageCoord, ImageLine


def segments_intersect(c1: Coord, c2: Coord, c3: Coord, c4: Coord) -> bool:
    """
    Finds if two segments intersect.

    :param c1: The 1st point of the 1st segment.
    :param c2: The 2nd point of the 1st segment.
    :param c3: The 1st point of the 2nd segment.
    :param c4: The 2nd point of the 2nd segment.
    """
    # https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines lol
    xdiff = Coord(c1.x - c2.x, c3.x - c4.x)
    ydiff = Coord(c1.y - c2.y, c3.y - c4.y)

    def det(a: Coord, b: Coord) -> float:
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

    :param coords: The list of coordinates
    :param float dash_length: the length of each dash
    :param float gap_length: the length of the gap between dashes
    """
    if dash_length <= 0.0 or gap_length <= 0.0:
        raise ValueError("dash or gap length cannot be <= 0")
    o_coords = tuple([c - coords.coords[0] for c in coords])
    return [
        ImageLine([a + coords.coords[0] for a in d])
        for d in _dash(o_coords, dash_length, gap_length)
    ]


@functools.cache
def _dash(
    coords: tuple[ImageCoord, ...],
    dash_length: float,
    gap_length: float,
) -> list[list[ImageCoord]]:
    dashes = []
    next_dash = []
    is_dash = True
    next_len = dash_length
    for c1, c2 in with_next(coords):
        if c1 == c2:
            continue
        cursor = c1
        while True:
            if is_dash:
                next_dash.append(cursor)
            new_cursor = cursor + (c2 - c1).unit() * next_len
            if (new_cursor - c2).dot(c2 - c1) >= 0:
                next_len -= abs(c2 - cursor)
                break

            cursor = new_cursor
            if is_dash:
                next_dash.append(cursor)
                dashes.append(next_dash.copy())
                next_dash.clear()
            is_dash = not is_dash
            next_len = dash_length if is_dash else gap_length
    if is_dash and len(coords) >= 1:
        next_dash.append(coords[-1])
        dashes.append(next_dash.copy())
    return dashes


def rotate_around_pivot(coord: Coord, pivot: Coord, theta: float) -> Coord:
    """
    Rotates a set of coordinates about a pivot point.

    :param float coord: The coordinate to be rotated
    :param float pivot: The pivot to be rotated about
    :param float theta: The angle to rotate in radians
    """
    coord_vec = vector.obj(x=coord.x, y=coord.y)
    pivot_vec = vector.obj(x=pivot.x, y=pivot.y)
    coord_vec -= pivot_vec
    new = coord_vec.rotateZ(theta)
    new += pivot_vec
    return Coord(new.x, new.y)
