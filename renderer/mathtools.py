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

def lines_intersect(c1: Coord, c2: Coord, c3: Coord, c4: Coord) -> bool:
    """
    Finds if two segments intersect.
    
    :param RealNum c1:  the 1st point of the 1st segment.
    :param RealNum c2:  the 2nd point of the 1st segment.
    :param RealNum c3:  the 1st point of the 2nd segment.
    :param RealNum c4:  the 2nd point of the 2nd segment.
        
    :returns: Whether the two segments intersect.
    :rtype: bool
    """
    # https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines lol
    xdiff = (c1.x - c2.x, c3.x - c4.x)
    ydiff = (c1.y - c2.y, c3.y - c4.y)
    det = lambda a, b: a[0] * b[1] - a[1] * b[0]
    return det(xdiff, ydiff) != 0

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
        if lines_intersect(c1, c2, c3, c4): return True
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
            if lines_intersect(c1, c2, c3, c4):
                return True
    for c in line:
        if top < c.x < bottom or left < c.y < right:
            return True
    return False

def new_dash(coords: list[Coord], dash_length: RealNum, gap_length: RealNum) -> list[tuple[Coord, Coord]]:
    if dash_length <= 0 or gap_length <= 0:
        raise ValueError("dash or gap length cannot be <= 0")
    predashes = [coords[0]]
    is_gap = False
    overflow = 0
    for c1, c2 in internal._with_next(coords):
        plotted_length = 0
        theta = math.atan2(c2.y-c1.y, c2.x-c1.x)
        dash_dx = round(dash_length * math.cos(theta), 10)
        dash_dy = round(dash_length * math.sin(theta), 10)
        gap_dx = round(gap_length * math.cos(theta), 10)
        gap_dy = round(gap_length * math.sin(theta), 10)
        if overflow != 0:
            pass # TODO make overflow = 0
        while overflow != 0:
            if is_gap:
                dx = gap_dx
                dy = gap_dy
            else:
                dx = dash_dx
                dy = dash_dy
            if (dx**2+dy**2)**0.5 > math.dist(c1, c2) - plotted_length:
                overflow = (dx**2+dy**2)**0.5 - (math.dist(c1, c2) - plotted_length)
                dx = round((math.dist(c1, c2) - plotted_length) * math.cos(theta), 10)
                dy = round((math.dist(c1, c2) - plotted_length) * math.sin(theta), 10)
            predashes.append(Coord(predashes[-1].x + dx, predashes[-1].y + dy))
            if overflow != 0:
                is_gap = False if is_gap else True


def dash(c1: Coord, c2: Coord, d: RealNum, g: RealNum, o: RealNum=0, empty_start: bool=False) -> list[list[Coord]]:
    """
    Finds points along a segment that are a specified distance apart.

    :param Coord c1: the 1st point
    :param Coord c2: the 2nd point
    :param RealNum d: the length of a single dash
    :param RealNum g: the length of the gap between dashes
    :param RealNum o: the offset from (c1.x,c1.y) towards (c2.x,c2.y) before dashes are calculated
    :param bool empty_start: Whether to start the line from (c1.x,c1.y) empty before the start of the next dash
        
    :returns: A list of points along the segment, given in [[(c1.x, c1.y), (c2.x, c2.y)], etc.]
    :rtype: list[list[Coord]]
    """
    if d <= 0 or g <= 0:
        raise ValueError("dash or gap length cannot be <= 0")
    m = None if c1.x == c2.x else (c2.y-c1.y)/(c2.x-c1.x)
    dash_ = []
    gap = False

    if o == 0:
        c3 = c1
    else:
        results = points_away(c1.x, c1.y, o, m)
        c3 = results[0] if min(c1.x, c2.x) <= results[0][0] <= max(c1.x, c2.x) and min(c1.y, c2.y) <= results[0][1] <= max(c1.y, c2.y) else results[1]
    if not empty_start and o != 0:
        dash_.append([Coord(c1.x, c1.y), Coord(c3.x, c3.y)])
        gap = True
    else:
        dash_.append([Coord(c3.x, c3.y)])

    while min(c1.x, c2.x) <= c3.x <= max(c1.x, c2.x) and min(c1.y, c2.y) <= c3.y <= max(c1.y, c2.y):
        if gap:
            results = points_away(c3.x, c3.y, g, m)
            if np.sign(c2.x-c1.x) == np.sign(results[0][0]-c1.x) and np.sign(c2.y-c1.y) == np.sign(results[0][1]-c1.y):
                if math.dist(results[0], (c1.x, c1.y)) > math.dist(results[1], (c1.x, c1.y)):
                    c3 = results[0]
                else:
                    c3 = results[1]
            else:
                c3 = results[1]
            #c3.x, c3.y = results[0] if np.sign(c2.x-c1.x) == np.sign(results[0][0]-c1.x) and np.sign(c2.y-c1.y) == np.sign(results[0][1]-c1.y) and math.dist(results[0], (c1.x,c1.y)) > math.dist(results[1], (c1.x,c1.y)) else results[1]
            dash_.append([c3])
            gap = False
        else:
            results = points_away(c3.x, c3.y, d, m)
            #print(results)
            #print(np.sign(c2.x-c1.x) == np.sign(results[0][0]-c1.x) and np.sign(c2.y-c1.y) == np.sign(results[0][1]-c1.y))
            if np.sign(c2.x-c1.x) == np.sign(results[0][0]-c1.x) and np.sign(c2.y-c1.y) == np.sign(results[0][1]-c1.y):
                if not (np.sign(c2.x-c1.x) == np.sign(results[1][0]-c1.x)
                        and np.sign(c2.y-c1.y) == np.sign(results[1][1]-c1.y))\
                        or math.dist(results[0], (c1.x, c1.y)) > math.dist(results[1], (c1.x, c1.y)):
                    c3 = results[0]
                else:
                    c3 = results[1]
            else:
                c3 = results[1]
            #c3.x, c3.y = results[0] if np.sign(c2.x-c1.x) == np.sign(results[0][0]-c1.x) and np.sign(c2.y-c1.y) == np.sign(results[0][1]-c1.y) and math.dist(results[0], (c1.x,c1.y)) > math.dist(results[1], (c1.x,c1.y)) else results[1]
            dash_[-1].append(c3)
            gap = True
    
    if len(dash_[-1]) == 1: # last is gap
        dash_.pop()
    else: # last is dash
        dash_[-1][1] = c2
        if dash_[-1][0] == dash_[-1][1]:
            dash_.pop()

    return dash_

def dash_offset(coords: list[Coord], d: RealNum, g: RealNum) -> list[tuple[RealNum, bool]]:
    """
    Calculates the offsets on each coord of a line for a smoother dashing sequence.

    :param List[Coord] coords: the coords of the line
    :param RealNum d: the length of a single dash
    :param RealNum g: the length of the gap between dashes

    :returns: The offsets of each coordinate, and whether to start the next segment with empty_start, given in (offset, empty_start)
    :rtype: list[tuple[RealNum, bool]]
   """
    o = 0
    offsets = [(0, False)]
    empty_start = False
    left = None
    for c in range(len(coords)-1):
        dashes = dash(coords[c], coords[c+1], d, g, o, empty_start)
        if not dashes: #line has no dashes
            prev = 0 if offsets == [] or left is None else left
            remnant = math.dist(coords[c], coords[c+1])
            o = abs(g - prev - remnant)
            left = prev + remnant
            empty_start = True
        elif dashes[0] == [coords[c], coords[c+1]]: #line is entirely dash
            prev = 0 if offsets == [] or left is None else left
            remnant = math.dist(coords[c], coords[c+1])
            o = abs(d - prev - remnant)
            left = prev + remnant
            empty_start = False
        else:
            last_coord = dashes[-1][1]
            if last_coord == coords[c+1]: #line ended with a dash
                if round(remnant := math.dist(dashes[-1][0], last_coord), 10) == d: #last dash is exactly d
                    left = 0
                    o = 0
                    empty_start = True
                else:
                    left = remnant
                    o = d - remnant
                    empty_start = False
            else: #line ended with a gap
                if round(remnant := math.dist(dashes[-1][0], coords[c+1]), 10) == g: #last gap is exactly g
                    left = 0
                    o = 0
                    empty_start = False
                else:
                    o = g - remnant
                    left = remnant
                    empty_start = True
        offsets.append((round(o, 2), empty_start))
    return offsets

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

def points_away(x: RealNum, y: RealNum, d: RealNum, m: RealNum | None) -> list[Coord]:
    """
    Finds two points that are a specified distance away from a specified point, all on a straight line.

    :param RealNum x: the x-coordinate of the original point
    :param RealNum y: the y-coordinate of the original point
    :param RealNum d: the distance the two points from the original point
    :param m: the gradient of the line. Give ``None`` for a gradient of undefined.
    :type m: RealNum | None

    :returns: Given in ``[c1, c2]``
    :rtype: list[Coord]
    """
    theta = math.atan(m) if m is not None else math.pi / 2
    dx = round(d*math.cos(theta), 10)
    dy = round(d*math.sin(theta), 10)
    return [Coord(x+dx, y+dy), Coord(x-dx, y-dy)]