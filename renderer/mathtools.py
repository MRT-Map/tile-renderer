import math
import numpy as np

from renderer.types import *
from typing import Optional, Tuple


def midpoint(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, o: RealNum, n: int=1, return_both: bool=False) -> Union[List[Tuple[Coord, RealNum]], List[List[Tuple[Coord, RealNum]]]]:
    """
    Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.
      
    :param RealNum x1: the x-coordinate of the 1st point
    :param RealNum y1: the y-coordinate of the 1st point
    :param RealNum x2: the x-coordinate of the 2nd point
    :param RealNum y2: the y-coordinate of the 2nd point
    :param RealNum o: the offset from the line. If positive, the point above the line is returned; if negative, the point below the line is returned
    :param int n: the number of midpoints on a single segment
    :param bool return_both: if True, it will return both possible points.
        
    :return: A list of *(lists of, when return_both=True)* tuples in the form of (x, y, rot)
    :rtype: list[tuple[Coord, RealNum]] *when return_both=False,* list[list[tuple[Coord, RealNum]]] *when return_both=True*
    """
    #print(x1, y1, x2, y2, o, n)
    points = []
    for p in range(1, n+1):
        x3, y3 = (x1+p*(x2-x1)/(n+1), y1+p*(y2-y1)/(n+1))
        #print(x3, y3)
        #x3, y3 = ((x1+x2)/2, (y1+y2)/2)
        if x1 == x2:
            m1 = None
            m2 = 0
        elif y1 == y2:
            m1 = 0
            m2 = None
        else:
            m1 = (y2-y1)/(x2-x1)
            m2 = -1 / m1
        results = points_away(x3, y3, o, m2)
        if return_both:
            #print(eq1, eq2)
            rot = 90 if x1 == x2 else math.degrees(-math.atan(m1))
            try:
                points += [(results[0][0], results[0][1], rot), (results[1][0], results[1][1], rot)]
            except IndexError:
                pass
        #print(results)
        elif x1 == x2:
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

def lines_intersect(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, x3: RealNum, y3: RealNum, x4: RealNum, y4: RealNum) -> bool:
    """
    Finds if two segments intersect.
    
    :param RealNum x1: the x-coordinate of the 1st point of the 1st segment.
    :param RealNum y1: the y-coordinate of the 1st point of the 1st segment.
    :param RealNum x2: the x-coordinate of the 2nd point of the 1st segment.
    :param RealNum y2: the y-coordinate of the 2nd point of the 1st segment.
    :param RealNum x3: the x-coordinate of the 1st point of the 2nd segment.
    :param RealNum y3: the y-coordinate of the 1st point of the 2nd segment.
    :param RealNum x4: the x-coordinate of the 2nd point of the 2nd segment.
    :param RealNum y4: the y-coordinate of the 2nd point of the 2nd segment.
        
    :returns: Whether the two segments intersect.
    :rtype: bool
    """
    # https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines lol
    xdiff = (x1 - x2, x3 - x4)
    ydiff = (y1 - y2, y3 - y4)
    det = lambda a, b: a[0] * b[1] - a[1] * b[0]
    return det(xdiff, ydiff) != 0

def point_in_poly(xp: RealNum, yp: RealNum, coords: List[Coord]) -> bool:
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
            
def poly_center(coords: List[Coord]) -> Coord:
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

def line_in_box(line: List[Coord], top: RealNum, bottom: RealNum, left: RealNum, right: RealNum) -> bool:
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
        x1, y1 = line[i]
        x2, y2 = line[i+1]
        for y3, x3, y4, x4 in [(top, left, bottom, left),
                               (bottom, left, bottom, right),
                               (bottom, right, top, right),
                               (top, right, top, left)]:
            if lines_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
                return True
    for x, y in line:
        if top < x < bottom or left < y < right:
            return True
    return False

def dash(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, d: RealNum, g: RealNum, o: RealNum=0, empty_start: bool=False) -> List[List[Coord]]:
    """
    Finds points along a segment that are a specified distance apart.
      
    :param RealNum x1: the x-coordinate of the 1st point
    :param RealNum y1: the y-coordinate of the 1st point
    :param RealNum x2: the x-coordinate of the 2nd point
    :param RealNum y2: the y-coordinate of the 2nd point
    :param RealNum d: the length of a single dash
    :param RealNum g: the length of the gap between dashes
    :param RealNum o: the offset from (x1,y1) towards (x2,y2) before dashes are calculated
    :param bool empty_start: Whether to start the line from (x1,y1) empty before the start of the next dash
        
    :returns: A list of points along the segment, given in [[(x1, y1), (x2, y2)], etc]
    :rtype: list[list[Coord]]
    """
    if d <= 0 or g <= 0:
        raise ValueError("dash or gap length cannot be <= 0")
    m = None if x1 == x2 else (y2-y1)/(x2-x1)
    dash_ = []
    gap = False

    if o == 0:
        x3, y3 = (x1, y1)
    else:
        results = points_away(x1, y1, o, m)
        x3, y3 = results[0] if min(x1, x2) <= results[0][0] <= max(x1, x2) and min(y1, y2) <= results[0][1] <= max(y1, y2) else results[1]
    if not empty_start and o != 0:
        dash_.append([Coord(x1, y1), Coord(x3, y3)])
        gap = True
    else:
        dash_.append([Coord(x3, y3)])

    while min(x1, x2) <= x3 <= max(x1, x2) and min(y1, y2) <= y3 <= max(y1, y2):
        if gap:
            results = points_away(x3, y3, g, m)
            if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1):
                if math.dist(results[0], (x1, y1)) > math.dist(results[1], (x1, y1)):
                    x3, y3 = results[0]
                else:
                    x3, y3 = results[1]
            else:
                x3, y3 = results[1]
            #x3, y3 = results[0] if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1) and math.dist(results[0], (x1,y1)) > math.dist(results[1], (x1,y1)) else results[1]
            dash_.append([Coord(x3, y3)])
            gap = False
        else:
            results = points_away(x3, y3, d, m)
            #print(results)
            #print(np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1))
            if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1):
                if not (np.sign(x2-x1) == np.sign(results[1][0]-x1)
                        and np.sign(y2-y1) == np.sign(results[1][1]-y1))\
                        or math.dist(results[0], (x1, y1)) > math.dist(results[1], (x1, y1)):
                    x3, y3 = results[0]
                else:
                    x3, y3 = results[1]
            else:
                x3, y3 = results[1]
            #x3, y3 = results[0] if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1) and math.dist(results[0], (x1,y1)) > math.dist(results[1], (x1,y1)) else results[1]
            dash_[-1].append(Coord(x3, y3))
            gap = True
    
    if len(dash_[-1]) == 1: # last is gap
        dash_.pop()
    else: # last is dash
        dash_[-1][1] = Coord(x2, y2)
        if dash_[-1][0] == dash_[-1][1]:
            dash_.pop()

    return dash_

def dash_offset(coords: List[Coord], d: RealNum, g: RealNum) -> List[Tuple[RealNum, bool]]:
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
        dashes = dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], d, g, o, empty_start)
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
            lastCoord = dashes[-1][1]
            if lastCoord == coords[c+1]: #line ended with a dash
                if round(remnant := math.dist(dashes[-1][0], lastCoord), 10) == d: #last dash is exactly d
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

def points_away(x: RealNum, y: RealNum, d: RealNum, m: Optional[RealNum]) -> List[Coord]:
    """
    Finds two points that are a specified distance away from a specified point, all on a straight line.

    :param RealNum x: the x-coordinate of the original point
    :param RealNum y: the y-coordinate of the original point
    :param RealNum d: the distance the two points from the original point
    :param m: the gradient of the line. Give ``None`` for a gradient of undefined.
    :type m: RealNum | None

    :returns: Given in ``[(x1, y1), (x2, y2)]``
    :rtype: list[Coord]
    """
    theta = math.atan(m) if m is not None else math.pi / 2
    dx = round(d*math.cos(theta), 10)
    dy = round(d*math.sin(theta), 10)
    return [Coord(x+dx, y+dy), Coord(x-dx, y-dy)]