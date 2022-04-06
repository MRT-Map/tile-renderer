from __future__ import annotations

import math
from itertools import product

import numpy as np

from renderer.types import *


def midpoint(c1: Coord, c2: Coord, o: RealNum, n: int = 1,
             return_both: bool = False) -> list[tuple[Coord, RealNum]] | list[list[tuple[Coord, RealNum]]]:
    """
    Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.
      
    :param RealNum c1: the 1st point
    :param RealNum c2: the 2nd point
    :param RealNum o: the offset from the line. If positive, the point above the line is returned; if negative, the point below the line is returned
    :param int n: the number of midpoints on a single segment
    :param bool return_both: if True, it will return both possible points.
        
    :return: A list of *(lists of, when return_both=True)* tuples in the form of (Coord, rot)
    :rtype: list[tuple[Coord, RealNum]] *when return_both=False,* list[list[tuple[Coord, RealNum]]] *when return_both=True*
    """
    #print(c1.x, c1.y, c2.x, c2.y, o, n)
    points = []
    for p in range(1, n+1):
        c3 = Coord(c1.x+p*(c2.x-c1.x)/(n+1), c1.y+p*(c2.y-c1.y)/(n+1))
        #print(c3.x, c3.y)
        #c3.x, c3.y = ((c1.x+c2.x)/2, (c1.y+c2.y)/2)
        if c1.x == c2.x:
            m1 = None
            m2 = 0
        elif c1.y == c2.y:
            m1 = 0
            m2 = None
        else:
            m1 = (c2.y-c1.y)/(c2.x-c1.x)
            m2 = -1 / m1
        results = points_away(c3.x, c3.y, o, m2)
        if return_both:
            #print(eq1, eq2)
            rot = 90 if c1.x == c2.x else math.degrees(-math.atan(m1))
            try:
                points += [(results[0][0], results[0][1], rot), (results[1][0], results[1][1], rot)]
            except IndexError:
                pass
        #print(results)
        elif c1.x == c2.x:
            if o < 0:
                c = results[0] if results[0][0] < results[1][0] else results[1]
            else:
                c = results[0] if results[0][0] > results[1][0] else results[1]
            rot = 90
            points.append((c, rot))
        else:
            if o < 0:
                c = results[0] if results[0][1] < results[1][1] else results[1]
            else:
                c = results[0] if results[0][1] > results[1][1] else results[1]
            rot = math.degrees(-math.atan(m1))
            points.append((c, rot))
    return points

def segments_intersect(c1: Coord, c2: Coord, c3: Coord, c4: Coord) -> bool:
    """
    Finds if two segments intersect.
    
    :param RealNum c1: the 1st point of the 1st segment.
    :param RealNum c2: the 2nd point of the 1st segment.
    :param RealNum c3: the 1st point of the 2nd segment.
    :param RealNum c4: the 2nd point of the 2nd segment.
        
    :returns: Whether the two segments intersect.
    :rtype: bool
    """
    # https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines lol
    xdiff = (c1.x - c2.x, c3.x - c4.x)
    ydiff = (c1.y - c2.y, c3.y - c4.y)
    det = lambda a, b: a[0] * b[1] - a[1] * b[0]
    div = det(xdiff, ydiff)
    if div == 0: return False
    d = (det(c1, c2), det(c3, c4))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return min(c1.x, c2.x) <= x <= max(c1.x, c2.x) and min(c1.y, c2.y) <= y <= max(c1.y, c2.y) \
        and min(c3.x, c4.x) <= x <= max(c3.x, c4.x) and min(c3.y, c4.y) <= y <= max(c3.y, c4.y)

def point_in_poly(xp: RealNum, yp: RealNum, coords: list[Coord]) -> bool:
    """
    Finds if a point is in a polygon.
        
    :param RealNum xp: the x-coordinate of the point.
    :param RealNum yp: the y-coordinate of the point.
    :param list[Coord] coords: the coordinates of the polygon; give in ``(x,y)``
        
    :returns: Whether the point is inside the polygon.
    :rtype: bool
    """
    if (xp, yp) in coords: return True
    coords = np.array(coords)
    xs = coords[:, 0] - xp
    ys = coords[:, 1] - yp
    bearings = np.diff(np.arctan2(ys, xs))
    bearings = np.where(bearings >= -math.pi, bearings, bearings + math.tau)
    bearings = np.where(bearings <= math.pi, bearings, bearings - math.tau)
    wind_num = round(bearings.sum()/math.tau)
    return wind_num != 0

def poly_intersect(poly1: list[Coord], poly2: list[Coord]) -> bool:
    coords1 = [i for i in internal._with_next(poly1)]
    coords2 = [i for i in internal._with_next(poly2)]
    for (c1, c2), (c3, c4) in product(coords1, coords2):
        if segments_intersect(c1, c2, c3, c4): return True
    if all(point_in_poly(x, y, poly2) for x, y in poly1): return True
    if all(point_in_poly(x, y, poly1) for x, y in poly2): return True
    return False

            
def poly_center(coords: list[Coord]) -> Coord:
    """
    Finds the center point of a polygon.
      
    :param list[Coord] coords: the coordinates of the polygon; give in ``(x,y)``
        
    :returns: The center of the polygon, given in ``(x,y)``
    :rtype: Coord
    """
    coords = np.array(coords)
    xs = np.array(np.meshgrid(coords[:, 0], coords[:, 0])).T.reshape(-1, 2)
    ys = np.array(np.meshgrid(coords[:, 1], coords[:, 1])).T.reshape(-1, 2)
    mx = (xs[:, 0]+xs[:, 1])/2
    my = (ys[:, 0]+ys[:, 1])/2
    return Coord(mx.sum()/len(mx), my.sum()/len(my))

def line_in_box(line: list[Coord], top: RealNum, bottom: RealNum, left: RealNum, right: RealNum) -> bool:
    """
    Finds if any nodes of a line go within the box.
      
    :param list[Coord] line: the line to check for
    :param RealNum top: the bounds of the box
    :param RealNum bottom: the bounds of the box
    :param RealNum left: the bounds of the box
    :param RealNum right: the bounds of the box
        
    :returns: Whether any nodes of a line go within the box.
    :rtype: bool
    """
    for i in range(len(line)-1):
        c1 = line[i]
        c2 = line[i+1]
        for c3, c4 in [(Coord(top, left), Coord(bottom, left)),
                       (Coord(bottom, left), Coord(bottom, right)),
                       (Coord(bottom, right), Coord(top, right)),
                       (Coord(top, right), Coord(top, left))]:
            if segments_intersect(c1, c2, c3, c4):
                return True
    for c in line:
        if top < c.x < bottom or left < c.y < right:
            return True
    return False

def dash(coords: list[Coord], dash_length: RealNum, gap_length: RealNum) -> list[tuple[Coord, Coord]]:
    """
    Takes a list of coordinates and returns a list of pairs of Coord objects.
    
    :param list[Coord] coords: the coordinates
    :param RealNum dash_length: the length of each dash
    :param RealNum gap_length:RealNum: the length of the gap between dashes
    :return: a list of pairs of Coords.
    """
    if dash_length <= 0 or gap_length <= 0:
        raise ValueError("dash or gap length cannot be <= 0")
    dashes = []
    is_gap = False
    overflow = 0
    for c1, c2 in internal._with_next(coords):
        predashes = [c1]
        plotted_length = 0
        start_as_gap = is_gap
        theta = math.atan2(c2.y-c1.y, c2.x-c1.x)
        dash_dx = dash_length * math.cos(theta)
        dash_dy = dash_length * math.sin(theta)
        gap_dx = gap_length * math.cos(theta)
        gap_dy = gap_length * math.sin(theta)
        if overflow != 0:
            if overflow > math.dist(c1, c2):
                predashes.append(c2)
                overflow -= math.dist(c1, c2)
                plotted_length += math.dist(c1, c2)
            else:
                overflow_x = overflow * math.cos(theta)
                overflow_y = overflow * math.sin(theta)
                predashes.append(Coord(predashes[-1].x + overflow_x, predashes[-1].y + overflow_y))
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
            if (dx**2+dy**2)**0.5 > math.dist(c1, c2) - plotted_length:
                overflow = (dx**2+dy**2)**0.5 - (math.dist(c1, c2) - plotted_length)
                predashes.append(c2)
            else:
                predashes.append(Coord(predashes[-1].x + dx, predashes[-1].y + dy))
                plotted_length += gap_length if is_gap else dash_length
                is_gap = False if is_gap else True
        for i, (c3, c4) in enumerate(internal._with_next(predashes[(1 if start_as_gap else 0):])):
            if i % 2 == 0 and c3 != c4: dashes.append((c3, c4))
    return dashes

def combine_edge_dashes(coords: list[tuple[Coord, Coord]]) -> list[tuple[Coord, ...]]:
    """
    Combines dashes at joints from the output of dash().

    :param coords: list of dashes.
    :type coords: list[tuple[Coord, Coord]]
    :return: list of combined dashes
    """
    new_coords = []
    prev_coord = None
    for c1, c2 in coords:
        if prev_coord != c1:
            new_coords.append((c1, c2))
        else:
            new_coords[-1] = (*new_coords[-1], c2)
        prev_coord = c2
    return new_coords

def rotate_around_pivot(x: RealNum, y: RealNum, px: RealNum, py: RealNum, theta: RealNum) -> Coord:
    """
    Rotates a set of coordinates around a pivot point.

    :param RealNum x: the x-coordinate to be rotated
    :param RealNum y: the y-coordinate to be rotated
    :param RealNum px: the x-coordinate of the pivot
    :param RealNum py: the y-coordinate of the pivot
    :param RealNum theta: how many **degrees** to rotate

    :returns: The rotated coordinates, given in ``(x,y)``
    :rtype: Coord
   """
    #provide θ in degrees
    theta = math.radians(theta)
    x -= px
    y -= py
    nx = x*math.cos(theta) - y*math.sin(theta)
    ny = y*math.cos(theta) + x*math.sin(theta)
    nx += px
    ny += py
    return Coord(nx, ny)

def points_away(x: RealNum, y: RealNum, d: RealNum, m: RealNum | None = None, theta: RealNum | None = None) -> tuple[Coord, Coord]:
    """
    Finds two points that are a specified distance away from a specified point, all on a straight line.

    :param RealNum x: the x-coordinate of the original point
    :param RealNum y: the y-coordinate of the original point
    :param RealNum d: the distance the two points from the original point
    :param m: the gradient of the line. Give ``None`` for a gradient of undefined.
    :type m: RealNum | None
    :param theta: The angle of the line from the horizontal, uses m if is None
    :type theta: RealNum | None

    :returns: Given in ``(c1, c2)``
    :rtype: tuple(Coord, Coord)
    """
    theta = theta if theta is not None else math.atan(m) if m is not None else math.pi / 2
    dx = d*math.cos(theta)
    dy = d*math.sin(theta)
    return Coord(x + dx, y + dy), Coord(x - dx, y - dy)

def offset(coords: list[Coord], d: RealNum) -> list[Coord]:
    """
    Returns a list of coordinates offset by d along its normal vector.

    :param list[Coord] coords: the coordinates
    :param RealNum d: the offset distance
    :rtype: list[Coord]
    """
    angles = [math.atan2(c2.y-c1.y, c2.x-c1.x) for c1, c2 in internal._with_next(coords)]
    offsetted_points_pairs = []
    for i, (a1, a2) in enumerate([(None, angles[0]), *internal._with_next(angles), (angles[-1], None)]):
        if a1 is None or a2 is None:
            # noinspection PyTypeChecker
            bisect_angle = a1+math.pi/2 if a1 is not None else a2+math.pi/2
        else:
            bisect_angle = (a1+a2+math.pi)/2
        offsetted_points_pairs.append(points_away(*coords[i], d, theta=bisect_angle))
    pc = offsetted_points_pairs[0][0] if offsetted_points_pairs[0][0].y > coords[0].y else offsetted_points_pairs[0][0] if offsetted_points_pairs[0][0].x > coords[0].x else offsetted_points_pairs[0][1]
    pc = offsetted_points_pairs[0][1] if pc == offsetted_points_pairs[0][0] and d < 0 else offsetted_points_pairs[0][0]
    pc = offsetted_points_pairs[0][0] if pc == offsetted_points_pairs[0][1] and d < 0 else offsetted_points_pairs[0][1]
    offsetted_points = [pc]
    for i, (c21, c22) in enumerate(offsetted_points_pairs[1:]):
        pc = offsetted_points[-1]
        if segments_intersect(c22, pc, coords[i], coords[i+1]):
            offsetted_points.append(c21)
        else:
            offsetted_points.append(c22)
    return offsetted_points
