import math
import sympy as sym
from typing import Union
import numpy as np

import renderer.internals.internal as internal
import renderer.tools as tools
import renderer.validate as validate
import renderer.misc as misc

def midpoint(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], o: Union[int, float], n=1, returnBoth=False):
    """
    Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.midpoint
    """
    #print(x1, y1, x2, y2, o, n)
    points = []
    for p in range(1, n+1):
        x3, y3 = (x1+p*(x2-x1)/(n+1),y1+p*(y2-y1)/(n+1))
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
        results = pointsAway(x3, y3, o, m2)
        if returnBoth:
            #print(eq1, eq2)
            rot = 90 if x1 == x2 else math.degrees(-math.atan(m1))
            try:
                points += [(results[0][0], results[0][1], rot), (results[1][0], results[1][1], rot)]
            except IndexError:
                pass
        #print(results)
        elif x1 == x2:
            if o < 0:
                x4, y4 = results[0] if results[0][0] < results[1][0] else results[1]
            else:
                x4, y4 = results[0] if results[0][0] > results[1][0] else results[1]
            rot = 90
            points.append((x4, y4, rot))
        else:
            if o < 0:
                x4, y4 = results[0] if results[0][1] < results[1][1] else results[1]
            else:
                x4, y4 = results[0] if results[0][1] > results[1][1] else results[1]
            rot = math.degrees(-math.atan(m1))
            points.append((x4, y4, rot))
    return points

def linesIntersect(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], x3: Union[int, float], y3: Union[int, float], x4: Union[int, float], y4: Union[int, float]):
    """
    Finds if two segments intersect.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.linesIntersect
    """
    xv, yv = sym.symbols('xv,yv')
    if x1 == x2:
        m1 = None
        eq1 = sym.Eq(xv,x1)
        c1 = None if x1 != 0 else math.inf
    else:
        m1 = (y2-y1)/(x2-x1)
        eq1 = sym.Eq(yv-y1,m1*(xv-x1))
        c1 = y1-m1*x1
    if x3 == x4:
        m2 = None
        eq2 = sym.Eq(xv,x3)
        c2 = None if x3 != 0 else math.inf
    else:
        m2 = (y4-y3)/(x4-x3)
        eq2 = sym.Eq(yv-y3,m2*(xv-x3))
        c2 = y3-m2*x3
    if m1 == m2 and c1 == c2: #same eq
        if x1 == x2:
            return False if (min(y1,y2)>max(y3,y4) and max(y1,x2)>min(y3,y4)) or (min(y3,y4)>max(y1,y2) and max(y3,y4)>min(y1,y2)) else True
        else:
            return False if (min(x1,x2)>max(x3,x4) and max(x1,x2)>min(x3,x4)) or (min(x3,x4)>max(x1,x2) and max(x3,x4)>min(x1,x2)) else True
    elif m1 == m2: #parallel
        return False
    #print(eq1, eq2)
    result = sym.solve([eq1, eq2], (xv, yv))
    if isinstance(result, list) and result != []:
        x5, y5 = result[0]
    elif isinstance(result, dict):
        x5 = result[xv]
        y5 = result[yv]
    else:
        return False
    x1 = round(x1, 10); x2 = round(x2, 10); x3 = round(x3, 10); x4 = round(x4, 10); x5 = round(x5, 10)
    y1 = round(y1, 10); y2 = round(y2, 10); y3 = round(y3, 10); y4 = round(y4, 10); y5 = round(y5, 10)
    return False if (x5>max(x1,x2) or x5<min(x1,x2) or y5>max(y1,y2) or y5<min(y1,y2) or x5>max(x3,x4) or x5<min(x3,x4) or y5>max(y3,y4) or y5<min(y3,y4)) else True

def pointInPoly(xp: Union[int, float], yp: Union[int, float], coords: list):
    """
    Finds if a point is in a polygon. WARNING: If your polygon has a lot of corners, this will take very long.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.pointInPoly
    """
    r = -math.inf
    for x, _ in coords:
        if x > r:
            r = x
    r += 10
    cross = 0
    for i in range(len(coords)):
        j = i + 1 if i != len(coords)-1 else 0
        if linesIntersect(coords[i][0], coords[i][1], coords[j][0], coords[j][1], xp, yp, r, yp):
            if coords[i][1] == yp:
                h = i - 1 if i != 0 else len(coords)-1
                cross += 0 if (coords[h][1]>yp and coords[i][1]>yp) or (coords[h][1]<yp and coords[i][1]<yp) else 0.5
            elif coords[j][1] == yp:
                k = j + 1 if j != len(coords)-1 else 0 
                cross += 0 if (coords[j][1]>yp and coords[k][1]>yp) or (coords[j][1]<yp and coords[k][1]<yp) else 0.5
            else:
                cross += 1
    return cross % 2 == 1
            
def polyCenter(coords: list):
    """
    Finds the center point of a polygon.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.polyCenter
    """
    mx = []
    my = []
    for x1, y1 in coords:
        for x2, y2 in coords:
            x3, y3, _ = midpoint(x1, y1, x2, y2, 0)[0]
            mx.append(x3)
            my.append(y3)
    return sum(mx)/len(mx), sum(my)/len(my)

def lineInBox(line: list, top: Union[int, float], bottom: Union[int, float], left: Union[int, float], right: Union[int, float]):
    """
    Finds if any nodes of a line go within the box.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.lineInBox
    """
    for i in range(len(line)-1):
        x1, y1 = line[i]
        x2, y2 = line[i+1]
        for y3, x3, y4, x4 in [(top,left,bottom,left), (bottom,left,bottom,right), (bottom,right,top,right), (top,right,top,left)]:
            if linesIntersect(x1, y1, x2, y2, x3, y3, x4, y4):
                return True
    for x,y in line:
        if top < x < bottom or left < y < right:
            return True
    return False

def dash(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], d: Union[int, float], g: Union[int, float], o=0, emptyStart=False):
    """
    Finds points along a segment that are a specified distance apart.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.dash
    """
    if d <= 0 or g <= 0:
        return ValueError("dash or gap length cannot be <= 0")
    m = None if x1 == x2 else (y2-y1)/(x2-x1)
    dash = []
    gap = False

    if o == 0:
        x3, y3 = (x1, y1)
    else:
        results = pointsAway(x1, y1, o, m)
        x3, y3 = results[0] if min(x1,x2) <= results[0][0] <= max(x1,x2) and min(y1,y2) <= results[0][1] <= max(y1,y2) else results[1]
    if not emptyStart and o != 0:
        dash.append([(x1, y1), (x3, y3)])
        gap = True
    else:
        dash.append([(x3, y3)])

    while min(x1,x2) <= x3 <= max(x1,x2) and min(y1,y2) <= y3 <= max(y1,y2):
        if gap:
            results = pointsAway(x3, y3, g, m)
            if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1):
                if math.dist(results[0], (x1,y1)) > math.dist(results[1], (x1,y1)):
                    x3, y3 = results[0]
                else:
                    x3, y3 = results[1]
            else:
                x3, y3 = results[1]
            #x3, y3 = results[0] if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1) and math.dist(results[0], (x1,y1)) > math.dist(results[1], (x1,y1)) else results[1]
            dash.append([(x3, y3)])
            gap = False
        else:
            results = pointsAway(x3, y3, d, m)
            #print(results)
            #print(np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1))
            if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1):
                if not (np.sign(x2-x1) == np.sign(results[1][0]-x1) and np.sign(y2-y1) == np.sign(results[1][1]-y1)) or math.dist(results[0], (x1,y1)) > math.dist(results[1], (x1,y1)):
                    x3, y3 = results[0]
                else:
                    x3, y3 = results[1]
            else:
                x3, y3 = results[1]
            #x3, y3 = results[0] if np.sign(x2-x1) == np.sign(results[0][0]-x1) and np.sign(y2-y1) == np.sign(results[0][1]-y1) and math.dist(results[0], (x1,y1)) > math.dist(results[1], (x1,y1)) else results[1]
            dash[-1].append((x3, y3))
            gap = True
    
    if len(dash[-1]) == 1: # last is gap
        dash.pop()
    else: # last is dash
        dash[-1][1] = (x2, y2)
        if dash[-1][0] == dash[-1][1]:
            dash.pop()

    return dash

def dashOffset(coords: list, d: Union[int, float], g: Union[int, float]):
    """
    Calculates the offsets on each coord of a line for a smoother dashing sequence.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.dashOffset
    """
    o = 0
    offsets = [(0, False)]
    emptyStart = False
    left = None
    for c in range(len(coords)-1):
        dashes = dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], d, g, o, emptyStart)
        if dashes == []: #line has no dashes
            prev = 0 if offsets == [] or left == None else left
            remnant = math.dist(coords[c], coords[c+1])
            o = abs(g - prev - remnant)
            left = prev + remnant
            emptyStart = True
        elif dashes[0] == [coords[c], coords[c+1]]: #line is entirely dash
            prev = 0 if offsets == [] or left == None else left
            remnant = math.dist(coords[c], coords[c+1])
            o = abs(d - prev - remnant)
            left = prev + remnant
            emptyStart = False
        else:
            lastCoord = dashes[-1][1]
            if lastCoord == coords[c+1]: #line ended with a dash
                if round(remnant := math.dist(dashes[-1][0], lastCoord), 10) == d: #last dash is exactly d
                    left = 0
                    o = 0
                    emptyStart = True
                else:
                    left = remnant
                    o = d - remnant
                    emptyStart = False
            else: #line ended with a gap
                if round(remnant := math.dist(dashes[-1][0], coords[c+1]), 10) == g: #last gap is exactly g
                    left = 0
                    o = 0
                    emptyStart = False
                else:
                    o = g - remnant
                    left = remnant
                    emptyStart = True
        offsets.append((round(o, 2), emptyStart))
    return offsets

def rotateAroundPivot(x: Union[int, float], y: Union[int, float], px: Union[int, float], py: Union[int, float], theta: Union[int, float]):
    """
    Rotates a set of coordinates around a pivot point.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.rotateAroundPivot
    """
    #provide θ in degrees
    theta = math.radians(theta)
    x -= px
    y -= py
    nx = x*math.cos(theta) - y*math.sin(theta)
    ny = y*math.cos(theta) + x*math.sin(theta)
    nx += px
    ny += py
    return nx, ny

def pointsAway(x: Union[int, float], y: Union[int, float], d: Union[int, float], m: Union[int, float]):
    """
    Finds two points that are a specified distance away from a specified point, all on a straight line.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.mathtools.pointsAway
    """
    theta = math.atan(m) if m != None else math.pi/2
    dx = round(d*math.cos(theta), 10)
    dy = round(d*math.sin(theta), 10)
    return [(x+dx, y+dy), (x-dx, y-dy)]