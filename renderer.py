#tile-renderer v1.0
from colorama import Fore, Style, init
import math
import json
from PIL import Image, ImageDraw, ImageFont
import sympy as sym
from typing import Union
import time
import glob
import re
import numpy as np
from schema import Schema, And, Or, Regex, Optional
init()

class utils:
    def coordListIntegrity(coords: list):
        for item in coords:
            if not isinstance(item, tuple):
                raise TypeError(f"Coordinates {item} is not type 'tuple'")
            elif len(item) != 2:
                raise ValueError(f"Coordinates {item} has {len(item)} values instead of 2")
            for n in item:
                if not isinstance(n, (int, float)):
                    raise TypeError(f"Coordinate {n} is not type 'int/float'")
        return True

    def tileCoordListIntegrity(tiles: list, minZoom: int, maxZoom: int):
        for item in tiles:
            if not isinstance(item, tuple):
                raise TypeError(f"Tile coordinates {item} is not type 'tuple'")
            elif len(item) != 3:
                raise ValueError(f"Tile coordinates {item} has {len(item)} values instead of 3")
            for n in item:
                if not isinstance(n, (int, float)):
                    raise TypeError(f"Tile coordinate {n} is not type 'int/float'")
            if not minZoom <= item[0] <= maxZoom:
                raise ValueError(f"Zoom value {item[0]} is not in the range {minZoom} <= z <= {maxZoom}")
            elif not isinstance(item[0], int):
                raise TypeError(f"Zoom value {item[0]} is not an integer")
        return True

    def nodeListIntegrity(nodes: list, nodeList: dict):
        for node in nodes:
            if not node in nodeList.keys():
                raise ValueError(f"Node '{node}' does not exist")

        return True

    def nodeJsonIntegrity(nodeList: dict):
        schema = Schema({
            str: {
                "x": Or(int, float),
                "y": Or(int, float),
                "connections": list
            }
        })
        schema.validate(nodeList)
        return True

    def plaJsonIntegrity(plaList: dict, nodeList: dict):
        schema = Schema({
            str: {
                "type": str,
                "displayname": str,
                "description": str,
                "layer": Or(int, float),
                "nodes": And(list, lambda i: utils.nodeListIntegrity(i, nodeList)),
                "attrs": dict
            }
        })
        schema.validate(plaList)
        return True
                
    def skinJsonIntegrity(skinJson: dict):
        mainSchema = Schema({
            "info": {
                "size": int,
                "font": {
                    "": str,
                    "b": str,
                    "i": str,
                    "bi": str
                },
                "background": And([int], lambda l: len(l) == 3 and not False in [0 <= n <= 255 for n in l])
            },
            "order": [str],
            "types": {
                str: {
                    "tags": list,
                    "type": lambda s: s in ['point', 'line', 'area'],
                    "style": {
                        str: list
                    }
                }
            }
        })
        point_circle = Schema({
            "layer": "circle",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "size": int,
            "width": int
        })
        point_text = Schema({
            "layer": "text",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "offset": And([int], lambda o: len(o) == 2),
            "size": int,
            "anchor": Or(None, str)
        })
        point_square = Schema({
            "layer": "square",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "size": int,
            "width": int
        })
        point_image = Schema({
            "layer": "image",
            "file": str,
            "offset": And([int], lambda o: len(o) == 2)
        })
        line_backfore = Schema({
            "layer": Or("back", "fore"),
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "width": int,
            Optional("dash"): And([int], lambda l: len(l) == 2)
        })
        line_text = Schema({
            "layer": "text",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "size": int,
            "offset": int
        })
        area_fill = Schema({
            "layer": "fill",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            Optional("stripe"): And([int], lambda l: len(l) == 3)
        })
        area_bordertext = Schema({
            "layer": "bordertext",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "offset": int,
            "size": int
        })
        area_centertext = Schema({
            "layer": "centertext",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "size": int,
            "offset": And(And(list, [int]), lambda o: len(o) == 2)
        })
        area_centerimage = Schema({
            "layer": "image",
            "file": str,
            "offset": And(And(list, [int]), lambda o: len(o) == 2)
        })

        schemas = {
            "point": {
                "circle": point_circle,
                "text": point_text,
                "square": point_square,
                "image": point_image
            },
            "line": {
                "text": line_text,
                "back": line_backfore,
                "fore": line_backfore
            },
            "area": {
                "bordertext": area_bordertext,
                "centertext": area_centertext,
                "fill": area_fill,
                "centerimage": area_centerimage
            }
        }

        mainSchema.validate(skinJson)
        for n, t in skinJson['types'].items():
            if not n in skinJson['order']:
                raise ValueError(f"Type {n} is not in order list")
            s = t['style']
            for z, steps in s.items():
                if internal.strToTuple(z)[0] > internal.strToTuple(z)[1]:
                    raise ValueError(f"Invalid range '{z}'")
                for step in steps:
                    if not step["layer"] in schemas[t['type']]:
                        raise ValueError(f"Invalid layer '{step}'")
                    else:
                        try:
                            schemas[t['type']][step['layer']].validate(step)
                        except Exception as e:
                            print(Fore.RED + f"Type {n}, range {z}, step {step['layer']}" + Style.RESET_ALL)
                            raise e

class internal:
    def log(msg: str, pLevel: int, vLevel: int):
        colour = {
            "0": Fore.GREEN,
            "1": "",
            "2": Style.DIM
        }
        if pLevel <= vLevel:
            print(colour[str(pLevel)] + msg + Style.RESET_ALL)

    def dictIndex(d: dict, v):
        return list(d.keys())[list(d.values()).index(v)]

    def readJson(file: str):
        with open(file, "r") as f:
            data = json.load(f)
            f.close()
            return data

    def writeJson(file: str, data: dict, pp=False):
        with open(file, "r+") as f:
            f.seek(0)
            f.truncate()
            if pp:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
            f.close()

    def tupleToStr(t: tuple):
        return str(t)[1:-1]

    def strToTuple(s: str):
        return tuple([int(x) for x in s.split(", ")])

    def msToTime(ms: Union[int, float]):
        if ms == 0:
            return "0ms"
        s = math.floor(ms / 1000)
        ms = round(ms % 1000, 2)
        m = math.floor(s / 60)
        s = s % 60
        h = math.floor(m / 60)
        m = m % 60
        d = math.floor(h / 24)
        h = h % 24
        res = ""
        if d != 0:
            res = res + str(d) + "d "
        if h != 0:
            res = res + str(h) + "h "
        if m != 0:
            res = res + str(m) + "min "
        if s != 0:
            res = res + str(s) + "s "
        if ms != 0:
            res = res + str(ms) + "ms "
        return res.strip()

class mathtools:
    def midpoint(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], o: Union[int, float], n=1, returnBoth=False):
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
            results = mathtools.pointsAway(x3, y3, o, m2)
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
        r = -math.inf
        for x, y in coords:
            if x > r:
                r = x
        r += 10
        cross = 0
        for i in range(len(coords)):
            j = i + 1 if i != len(coords)-1 else 0
            if mathtools.linesIntersect(coords[i][0], coords[i][1], coords[j][0], coords[j][1], xp, yp, r, yp):
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
        mx = []
        my = []
        for x1, y1 in coords:
            for x2, y2 in coords:
                x3, y3, r = mathtools.midpoint(x1, y1, x2, y2, 0)[0]
                mx.append(x3)
                my.append(y3)
        return sum(mx)/len(mx), sum(my)/len(my)

    def lineInBox(line: list, top: Union[int, float], bottom: Union[int, float], left: Union[int, float], right: Union[int, float]):
        for i in range(len(line)-1):
            x1, y1 = line[i]
            x2, y2 = line[i+1]
            for y3, x3, y4, x4 in [(top,left,bottom,left), (bottom,left,bottom,right), (bottom,right,top,right), (top,right,top,left)]:
                if mathtools.linesIntersect(x1, y1, x2, y2, x3, y3, x4, y4):
                    return True
        for x,y in line:
            if top < x < bottom or left < y < right:
                return True
        return False

    def dash(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], d: Union[int, float], g: Union[int, float], o=0, emptyStart=False):
        if d <= 0 or g <= 0:
            return ValueError("dash or gap length cannot be <= 0")
        m = None if x1 == x2 else (y2-y1)/(x2-x1)
        dash = []
        gap = False

        if o == 0:
            x3, y3 = (x1, y1)
        else:
            results = mathtools.pointsAway(x1, y1, o, m)
            x3, y3 = results[0] if min(x1,x2) <= results[0][0] <= max(x1,x2) and min(y1,y2) <= results[0][1] <= max(y1,y2) else results[1]
        if not emptyStart and o != 0:
            dash.append([(x1, y1), (x3, y3)])
            gap = True
        else:
            dash.append([(x3, y3)])

        while min(x1,x2) <= x3 <= max(x1,x2) and min(y1,y2) <= y3 <= max(y1,y2):
            if gap:
                results = mathtools.pointsAway(x3, y3, g, m)
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
                results = mathtools.pointsAway(x3, y3, d, m)
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
        o = 0
        offsets = [(0, False)]
        emptyStart = False
        left = None
        for c in range(len(coords)-1):
            dashes = mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], d, g, o, emptyStart)
            if dashes == []: #line has no dashes
                prev = 0 if offsets == [] else left
                remnant = math.dist(coords[c], coords[c+1])
                o = abs(g - prev - remnant)
                left = prev + remnant
                emptyStart = True
            elif dashes[0] == [coords[c], coords[c+1]]: #line is entirely dash
                prev = 0 if offsets == [] else left
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
        theta = math.atan(m) if m != None else math.pi/2
        dx = round(d*math.cos(theta), 10)
        dy = round(d*math.sin(theta), 10)
        return [(x+dx, y+dy), (x-dx, y-dy)]

class tools:
    def tile_findEnds(coords: list):
        xMax = -math.inf
        xMin = math.inf
        yMax = -math.inf
        yMin = math.inf
        for z, x, y in coords:
            xMax = x if x > xMax else xMax
            xMin = x if x < xMin else xMin
            yMax = y if y > yMax else yMax
            yMin = y if y < yMin else yMin
        return xMax, xMin, yMax, yMin

    def line_findEnds(coords: list):
        xMax = -math.inf
        xMin = math.inf
        yMax = -math.inf
        yMin = math.inf
        for x, y in coords:
            xMax = x if x > xMax else xMax
            xMin = x if x < xMin else xMin
            yMax = y if y > yMax else yMax
            yMin = y if y < yMin else yMin
        return xMax, xMin, yMax, yMin

    def findPlasAttachedToNode(nodeId: str, plaList: dict):
        plas = []
        for plaId, pla in plaList.items():
            #print(plaId)
            if nodeId in pla['nodes']:
                plas.append((plaId, pla['nodes'].index(nodeId)))
        return plas

    def nodesToCoords(nodes: list, nodeList: dict):
        coords = []
        for nodeid in nodes:
            if not nodeid in nodeList.keys():
                raise KeyError(f"Node '{nodeid}' does not exist")
            coords.append((nodeList[nodeid]['x'],nodeList[nodeid]['y']))
        return coords
    
    def plaJson_findEnds(plaList: dict, nodeList: dict):
        xMax = -math.inf
        xMin = math.inf
        yMax = -math.inf
        yMin = math.inf
        for pla in plaList.keys():
            coords = tools.nodesToCoords(plaList[pla]['nodes'], nodeList)
            for x, y in coords:
                xMax = x if x > xMax else xMax
                xMin = x if x < xMin else xMin
                yMax = y if y > yMax else yMax
                yMin = y if y < yMin else yMin
        return xMax, xMin, yMax, yMin

    def plaJson_calcRenderedIn(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int):
        if maxZoom < minZoom:
            raise ValueError("Max zoom value is lesser than min zoom value")

        tiles = []
        for pla in plaList.keys():
            coords = tools.nodesToCoords(plaList[pla]['nodes'], nodeList)
            tiles.extend(tools.lineToTiles(coords, minZoom, maxZoom, maxZoomRange))

        return tiles

    def coordToTiles(coord: list, minZoom: int, maxZoom: int, maxZoomRange: int):
        if maxZoom < minZoom:
            raise ValueError("Max zoom value is lesser than min zoom value")

        tiles = []
        for z in reversed(range(minZoom, maxZoom+1)):
            x = math.floor(coord[0] / maxZoomRange)
            y = math.floor(coord[1] / maxZoomRange)
            tiles.append((z,x,y))
            maxZoomRange *= 2

        return tiles
        

    def lineToTiles(coords: list, minZoom: int, maxZoom: int, maxZoomRange: int):
        if len(coords) == 0:
            raise ValueError("Empty list of coords given")
        elif maxZoom < minZoom:
            raise ValueError("Max zoom value is lesser than min zoom value")
        
        tiles = []
        xMax = -math.inf
        xMin = math.inf
        yMax = -math.inf
        yMin = math.inf
        
        for x, y in coords:
            xMax = x+10 if x > xMax else xMax
            xMin = x-10 if x < xMin else xMin
            yMax = y+10 if y > yMax else yMax
            yMin = y-10 if y < yMin else yMin
        xr = list(range(xMin, xMax+1, int(maxZoomRange/2)))
        xr.append(xMax+1)
        yr = list(range(yMin, yMax+1, int(maxZoomRange/2)))
        yr.append(yMax+1)
        for x in xr:
            for y in yr:
                tiles.extend(tools.coordToTiles([x,y], minZoom, maxZoom, maxZoomRange))
        tiles = list(dict.fromkeys(tiles))
        return tiles

def tileMerge(images: Union[str, dict], verbosityLevel=1, saveImages=True, saveDir="tiles/", zoom=[]):
    tileReturn = {}
    if isinstance(images, str):
        imageDict = {}
        for d in glob.glob(images+"*.png"):
            regex = re.search(fr"^{images}(-?\d+, -?\d+, -?\d+)\.png$", d)
            if regex == None:
                continue
            coord = regex.group(1)
            i = Image.open(d)
            imageDict[coord] = i
            internal.log(f"Retrieved {coord}", 1, verbosityLevel)
    else:
        imageDict = images
    internal.log("Retrieved all images", 0, verbosityLevel)
    
    if zoom == []:
        minZoom = math.inf
        maxZoom = -math.inf
        for c in imageDict.keys():
            z = internal.strToTuple(c)[0]
            minZoom = z if z < minZoom else minZoom
            maxZoom = z if z > maxZoom else maxZoom
    else:
        minZoom = min(zoom)
        maxZoom = max(zoom)
    internal.log("Zoom levels determined", 0, verbosityLevel)
    for z in range(minZoom, maxZoom+1):
        toMerge = {}
        for c, i in imageDict.items():
            #i = imageDict[c]
            if internal.strToTuple(c)[0] == z:
                toMerge[c] = i
                internal.log(f"Zoom {z} will include {c}", 1, verbosityLevel)
        internal.log(f"Zoom {z}: Tiles to be merged determined", 0, verbosityLevel)
        tileCoords = [internal.strToTuple(s) for s in toMerge.keys()]
        #print(tileCoords)
        xMax, xMin, yMax, yMin = tools.tile_findEnds(tileCoords)
        #print(imageDict.values())
        tileSize = list(imageDict.values())[0].size[0]
        i = Image.new('RGBA', (tileSize*(xMax-xMin+1), tileSize*(yMax-yMin+1)), (0, 0, 0, 0))
        px = 0
        py = 0
        for x in range(xMin, xMax+1):
            for y in range(yMin, yMax+1):
                if f"{z}, {x}, {y}" in toMerge.keys():
                    i.paste(toMerge[f"{z}, {x}, {y}"], (px, py))
                    internal.log(f"{z}, {x}, {y} pasted", 1, verbosityLevel)
                py += tileSize
            px += tileSize
            py = 0
        #tileReturn[tilePlas] = im
        if saveImages:
            i.save(f'{saveDir}merge_{z}.png', 'PNG')
        tileReturn[str(z)] = i
        internal.log(f"Zoom {z} merged", 0, verbosityLevel)
        
    internal.log("All merges complete", 0, verbosityLevel)
    return tileReturn
        

def render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, verbosityLevel=1, saveImages=True, saveDir="", assetsDir="skins/assets/", **kwargs):
    if maxZoom < minZoom:
        raise ValueError("Max zoom value is greater than min zoom value")
    tileReturn = {}
    
    # integrity checks
    internal.log("Validating skin...", 0, verbosityLevel)
    utils.skinJsonIntegrity(skinJson)
    internal.log("Validating PLAs...", 0, verbosityLevel)
    utils.plaJsonIntegrity(plaList, nodeList)
    internal.log("Validating nodes...", 0, verbosityLevel)
    utils.nodeJsonIntegrity(nodeList)

    #finds which tiles to render
    if 'tiles' in kwargs.keys() and isinstance(kwargs['tiles'], list):
        tiles = kwargs['tiles']
        utils.tileCoordListIntegrity(tiles, minZoom, maxZoom)
    else: #finds box of tiles
        xMax, xMin, yMax, yMin = tools.plaJson_findEnds(plaList, nodeList)
        tiles = tools.lineToTiles([(xMax,yMax),(xMin,yMax),(xMax,yMin),(xMin,yMin)], minZoom, maxZoom, maxZoomRange)
    internal.log("Tiles to be generated found", 2, verbosityLevel)

    #sort PLAs by tiles
    tileList = {}
    for tile in tiles:
        tileList[internal.tupleToStr(tile)] = {}
    for pla in plaList.keys():
        coords = tools.nodesToCoords(plaList[pla]['nodes'], nodeList)
        renderedIn = tools.lineToTiles(coords, minZoom, maxZoom, maxZoomRange)
        for tile in renderedIn:
            if internal.tupleToStr(tile) in tileList.keys():
                tileList[internal.tupleToStr(tile)][pla] = plaList[pla]
    internal.log("Sorted PLA by tiles", 2, verbosityLevel)
    
    #print(tileList)
    
    processStart = time.time() * 1000
    processed = 0
    internal.log("Starting processing...", 0, verbosityLevel)
    for tilePlas in tileList.keys():
        #sort PLAs in tiles by layer
        newTilePlas = {}
        for pla in tileList[tilePlas].keys():
            if not str(float(tileList[tilePlas][pla]['layer'])) in newTilePlas.keys():
                newTilePlas[str(float(tileList[tilePlas][pla]['layer']))] = {}
            newTilePlas[str(float(tileList[tilePlas][pla]['layer']))][pla] = tileList[tilePlas][pla]
        internal.log(f"{tilePlas}: Sorted PLA by layer", 2, verbosityLevel)

        #sort PLAs in layers in files by type
        for layer in newTilePlas.keys():
            #print(newTilePlas[layer].items())
            newTilePlas[layer] = {k: v for k, v in sorted(newTilePlas[layer].items(), key=lambda x: skinJson['order'].index(x[1]['type'].split(' ')[0]))}
        internal.log(f"{tilePlas}: Sorted PLA by type", 2, verbosityLevel)
        
        #merge layers
        tileList[tilePlas] = {}
        layers = sorted(newTilePlas.keys(), key=lambda x: float(x))
        for layer in layers:
            for key, pla in newTilePlas[layer].items():
                tileList[tilePlas][key] = pla
        internal.log(f"{tilePlas}: Merged layers", 2, verbosityLevel)
        
        #print(newTilePlas)
        #print(tileList[tilePlas])

        #groups PLAs of the same type if "road" tag present
        newerTilePlas = [{}]
        keys = list(tileList[tilePlas].keys())
        for i in range(len(tileList[tilePlas])):
            newerTilePlas[-1][keys[i]] = tileList[tilePlas][keys[i]]
            if i != len(keys)-1 and (tileList[tilePlas][keys[i+1]]['type'].split(' ')[0] != tileList[tilePlas][keys[i]]['type'].split(' ')[0] or not "road" in skinJson['types'][tileList[tilePlas][keys[i]]['type'].split(' ')[0]]['tags']):
                newerTilePlas.append({})
        tileList[tilePlas] = newerTilePlas
        internal.log("PLAs grouped", 2, verbosityLevel)

        processed += 1
        timeLeft = round(((int(round(time.time() * 1000)) - processStart) / processed * (len(tileList) - processed)), 2)
        #logging.info('tile %d/%d [%d, %d] (%s left)', processed, len(tileList), x, y, msToTime(timeLeft))
        internal.log(f"Processed {tilePlas} ({round(processed/len(tileList)*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel)
    
    #count # of rendering operations
    internal.log("Counting no. of operations...", 0, verbosityLevel)
    operations = 0
    for tilePlas in tileList.keys():
        if tileList[tilePlas] == [{}]:
            continue

        for group in tileList[tilePlas]:
            info = skinJson['types'][list(group.values())[0]['type'].split(" ")[0]]
            style = []
            for zoom in info['style'].keys():
                if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tilePlas)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                    style = info['style'][zoom]
                    break
            for step in style:
                for plaId, pla in group.items():
                    operations += 1
                if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                    operations += 1
        operations += 1 #text
        internal.log(f"{tilePlas} counted", 2, verbosityLevel)
    
    #render
    operated = 0
    renderStart = time.time() * 1000
    internal.log("Starting render...", 0, verbosityLevel)
    for tilePlas in tileList.keys():
        if tileList[tilePlas] == [{}]:
            if operated != 0:
                timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
                internal.log(f"Rendered {tilePlas} ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 0, verbosityLevel)
            else:
                internal.log(f"Rendered {tilePlas}", 0, verbosityLevel)
            continue
        
        size = maxZoomRange*2**(maxZoom-internal.strToTuple(tilePlas)[0])
        im = Image.new(mode = "RGBA", size = (skinJson['info']['size'], skinJson['info']['size']), color = tuple(skinJson['info']['background']))
        img = ImageDraw.Draw(im)
        textList = []
        pointsTextList = []
        internal.log(f"{tilePlas}: Initialised canvas", 2, verbosityLevel)

        def getFont(f: str, s: int):
            if f in skinJson['info']['font'].keys():
                return ImageFont.truetype(assetsDir+skinJson['info']['font'][f], s)
            raise ValueError

        #im.save(f'tiles/{tilePlas}.png', 'PNG')
        for group in tileList[tilePlas]:
            info = skinJson['types'][list(group.values())[0]['type'].split(" ")[0]]
            style = []
            for zoom in info['style'].keys():
                if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tilePlas)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                    style = info['style'][zoom]
                    break
            for step in style:
                for plaId, pla in group.items():
                    coords = [(x - internal.strToTuple(tilePlas)[1] * size, y - internal.strToTuple(tilePlas)[2] * size) for x, y in tools.nodesToCoords(pla['nodes'], nodeList)]
                    coords = [(int(skinJson['info']['size'] / size * x), int(skinJson['info']['size'] / size * y)) for x, y in coords]
                    
                    def point_circle():
                        img.ellipse([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2], fill=step['colour'], outline=step['outline'], width=step['width'])

                    def point_text():
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        i = Image.new('RGBA', (2*textLength,2*(step['size']+4)), (0, 0, 0, 0))
                        d = ImageDraw.Draw(i)
                        d.text((textLength, step['size']+4), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                        tw, th = i.size
                        pointsTextList.append((i, coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1], tw, th, 0))
                        # font = getFont("", step['size'])
                        # img.text((coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1]), pla['displayname'], fill=step['colour'], font=font, anchor=step['anchor'])

                    def point_square():
                        img.rectangle([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2], fill=step['colour'], outline=step['outline'], width=step['width'])

                    def point_image():
                        icon = Image.open(assetsDir+step['file'])
                        im.paste(icon, (int(coords[0][0]-icon.width/2+step['offset'][0]), int(coords[0][1]-icon.height/2+step['offset'][1])), icon)

                    def line_text():
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        if textLength == 0:
                            textLength = int(img.textlength("----------", font))
                        internal.log(f"{tilePlas}: {plaId}: Text length calculated", 2, verbosityLevel)
                        for c in range(len(coords)-1):
                            #print(coords)
                            #print(mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']))
                            t = math.floor(math.dist(coords[c], coords[c+1])/(4*textLength))
                            t = 1 if t == 0 else t
                            if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= math.dist(coords[c], coords[c+1]):
                                #print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset']))     
                                for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=t):
                                    i = Image.new('RGBA', (2*textLength,2*(step['size']+4)), (0, 0, 0, 0))
                                    d = ImageDraw.Draw(i)
                                    d.text((textLength, step['size']+4), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                                    tw, th = i.size[:]
                                    i = i.rotate(trot, expand=True)
                                    textList.append((i, tx, ty, tw, th, trot))
                                internal.log(f"{tilePlas}: {plaId}: Name text generated", 2, verbosityLevel)
                            if "oneWay" in pla['type'].split(" ")[1:] and textLength <= math.dist(coords[c], coords[c+1]):
                                getFont("b", step['size'])
                                counter = 0
                                t = math.floor(math.dist(coords[c], coords[c+1])/(4*textLength))
                                for tx, ty, useless in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=2*t+1):
                                    if counter % 2 == 1:
                                        counter += 1
                                        continue
                                    trot = math.degrees(math.atan2(coords[c+1][0]-coords[c][0], coords[c+1][1]-coords[c][1]))
                                    i = Image.new('RGBA', (2*textLength,2*(step['size']+4)), (0, 0, 0, 0))
                                    d = ImageDraw.Draw(i)
                                    d.text((textLength, step['size']+4), "↓", fill=step['colour'], font=font, anchor="mm")
                                    tw, th = i.size[:]
                                    i = i.rotate(trot, expand=True)
                                    textList.append((i, tx, ty, tw, th, trot))
                                    counter += 1
                                internal.log(f"{tilePlas}: {plaId}: Oneway arrows generated", 2, verbosityLevel)
                                
                    def line_backfore():
                        if not "dash" in step.keys():
                            img.line(coords, fill=step['colour'], width=step['width'])
                            internal.log(f"{tilePlas}: {plaId}: Line drawn", 2, verbosityLevel)
                            for x, y in coords:
                                if not ("unroundedEnds" in info['tags'] and coords.index((x,y)) in [0, len(coords)-1]):
                                    img.ellipse([x-step['width']/2+1, y-step['width']/2+1, x+step['width']/2, y+step['width']/2], fill=step['colour'])
                            internal.log(f"{tilePlas}: {plaId}: Joints drawn", 2, verbosityLevel)
                        else:
                            offsetInfo = mathtools.dashOffset(coords, step['dash'][0], step['dash'][1])
                            #print(offsetInfo)
                            for c in range(len(coords)-1):
                                o, emptyStart = offsetInfo[c]
                                for dashCoords in mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['dash'][0], step['dash'][1], o, emptyStart):
                                    #print(dashCoords)
                                    img.line(dashCoords, fill=step['colour'], width=step['width'])                
                                internal.log(f"{tilePlas}: {plaId}: Dashes drawn for section {c+1} of {len(coords)}", 2, verbosityLevel)
                            internal.log(f"{tilePlas}: {plaId}: Dashes drawn", 2, verbosityLevel)

                    def area_bordertext():
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        internal.log(f"{tilePlas}: {plaId}: Text length calculated", 2, verbosityLevel)
                        for c1 in range(len(coords)):
                            c2 = c1+1 if c1 != len(coords)-1 else 0
                            if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= math.dist(coords[c1], coords[c2]):
                                #coords[c]
                                t = math.floor(math.dist(coords[c1], coords[c2])/(4*textLength))
                                t = 1 if t == 0 else t
                                allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1], step['offset'], n=t, returnBoth=True)
                                internal.log(f"{tilePlas}: {plaId}: Midpoints calculated", 2, verbosityLevel)
                                for n in range(0, len(allPoints), 2):
                                    points = [allPoints[n], allPoints[n+1]]
                                    if step['offset'] < 0:
                                        tx, ty, trot = points[0] if not mathtools.pointInPoly(points[0][0], points[0][1], coords) else points[1]
                                    else:
                                        #print(points[0][0], points[0][1], coords)
                                        #print(mathtools.pointInPoly(points[0][0], points[0][1], coords))
                                        tx, ty, trot = points[0] if mathtools.pointInPoly(points[0][0], points[0][1], coords) else points[1]
                                    i = Image.new('RGBA', (2*textLength,2*(step['size']+4)), (0, 0, 0, 0))
                                    d = ImageDraw.Draw(i)
                                    d.text((textLength, step['size']+4), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                                    tw, th = i.size[:]
                                    i = i.rotate(trot, expand=True)
                                    textList.append((i, tx, ty, tw, th, trot))
                                    internal.log(f"{tilePlas}: {plaId}: Text {n+1} of {len(allPoints)} generated in section {c1} of {len(coords)+1}", 2, verbosityLevel)

                    def area_centertext():
                        cx, cy = mathtools.polyCenter(coords)
                        internal.log(f"{tilePlas}: {plaId}: Center calculated", 2, verbosityLevel)
                        cx += step['offset'][0]
                        cy += step['offset'][1]
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        i = Image.new('RGBA', (2*textLength,2*(step['size']+4)), (0, 0, 0, 0))
                        d = ImageDraw.Draw(i)
                        cw, ch = i.size
                        d.text((textLength, step['size']+4), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                        textList.append((i, cx, cy, cw, ch, 0))

                    def area_fill():
                        if "stripe" in step.keys():
                            xMax, xMin, yMax, yMin = tools.line_findEnds(coords)
                            xMax += xMax-xMin
                            xMin -= yMax-yMin
                            yMax += xMax-xMin
                            yMin -= yMax-yMin
                            i = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                            d = ImageDraw.Draw(i)
                            tlx = xMin-1
                            while tlx <= xMax:
                                d.polygon([(tlx, yMin), (tlx+step['stripe'][0], yMin), (tlx+step['stripe'][0], yMax), (tlx, yMax)], fill=step['colour'])
                                tlx += step['stripe'][0]+step['stripe'][1]
                            internal.log(f"{tilePlas}: {plaId}: Stripes generated", 2, verbosityLevel)
                            i = i.rotate(step['stripe'][2], center=mathtools.polyCenter(coords))
                            mi = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                            md = ImageDraw.Draw(mi)
                            md.polygon(coords, fill=step['colour'])
                            pi = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                            pi.paste(i, (0, 0), mi)
                            im.paste(pi, (0, 0), pi)
                        else:
                            img.polygon(coords, fill=step['colour'], outline=step['outline'])
                        internal.log(f"{tilePlas}: {plaId}: Area filled", 2, verbosityLevel)
                        outlineCoords = coords[:]
                        outlineCoords.append(outlineCoords[0])
                        img.line(outlineCoords, fill=step['colour'], width=4)
                        for x, y in outlineCoords:
                            if not ("unroundedEnds" in info['tags'] and outlineCoords.index((x,y)) in [0, len(outlineCoords)-1]):
                                img.ellipse([x-4/2+1, y-4/2+1, x+4/2, y+4/2], fill=step['colour'])
                        internal.log(f"{tilePlas}: {plaId}: Outline drawn", 2, verbosityLevel)

                    def area_centerimage():
                        x, y = mathtools.polyCenter(coords)
                        icon = Image.open(assetsDir+step['file'])
                        im.paste(i, (x+step['offset'][0], y+step['offset'][1]), icon)

                    funcs = {
                        "point": {
                            "circle": point_circle,
                            "text": point_text,
                            "square": point_square,
                            "image": point_image
                        },
                        "line": {
                            "text": line_text,
                            "back": line_backfore,
                            "fore": line_backfore
                        },
                        "area": {
                            "bordertext": area_bordertext,
                            "centertext": area_centertext,
                            "fill": area_fill,
                            "centerimage": area_centerimage
                        }
                    }

                    if step['layer'] not in funcs[info['type']].keys():
                        raise KeyError(f"{step['layer']} is not a valid layer")
                    funcs[info['type']][step['layer']]()

                    operated += 1
                    timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
                    internal.log(f"Rendered step {style.index(step)+1} of {len(style)} of {plaId} ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel)

                if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                    nodes = []
                    for pla in group.values():
                        nodes += pla['nodes']
                    connectedPre = [tools.findPlasAttachedToNode(x, plaList) for x in nodes]
                    connected = []
                    for i in connectedPre:
                       connected += i
                    internal.log(f"{tilePlas}: Connected lines found", 2, verbosityLevel)
                    for conPla, index in connected:
                        if not "road" in skinJson['types'][plaList[conPla]['type'].split(" ")[0]]['tags']:
                            continue
                        conInfo = skinJson['types'][plaList[conPla]['type'].split(" ")[0]]
                        conStyle = []
                        for zoom in conInfo['style'].keys():
                            if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tilePlas)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                                conStyle = conInfo['style'][zoom]
                                break
                        for conStep in conStyle:
                            if conStep['layer'] in ["back", "text"]:
                                continue
                            
                            conCoords = [(x-internal.strToTuple(tilePlas)[1]*size, y-internal.strToTuple(tilePlas)[2]*size) for x,y in tools.nodesToCoords(plaList[conPla]['nodes'], nodeList)]
                            conCoords = [(int(skinJson['info']['size']/size*x), int(skinJson['info']['size']/size*y)) for x,y in conCoords]
                            preConCoords = conCoords[:]
                            internal.log(f"{tilePlas}: Coords extracted", 2, verbosityLevel)

                            if index == 0:
                                conCoords = [conCoords[0], conCoords[1]]
                                if not "dash" in conStep.keys():
                                    conCoords[1] = ((conCoords[0][0]+conCoords[1][0])/2, (conCoords[0][1]+conCoords[1][1])/2)
                            elif index == len(conCoords)-1:
                                conCoords = [conCoords[index-1], conCoords[index]]
                                if not "dash" in conStep.keys():
                                    conCoords[0] = ((conCoords[0][0]+conCoords[1][0])/2, (conCoords[0][1]+conCoords[1][1])/2)
                            else:
                                conCoords = [conCoords[index-1], conCoords[index], conCoords[index+1]]
                                if not "dash" in conStep.keys():
                                    conCoords[0] = ((conCoords[0][0]+conCoords[1][0])/2, (conCoords[0][1]+conCoords[1][1])/2)
                                    conCoords[2] = ((conCoords[2][0]+conCoords[1][0])/2, (conCoords[2][1]+conCoords[1][1])/2)
                            internal.log(f"{tilePlas}: Coords processed", 2, verbosityLevel)
                            if not "dash" in conStep.keys():
                                img.line(conCoords, fill=conStep['colour'], width=conStep['width'])
                                for x, y in conCoords:
                                    img.ellipse([x-conStep['width']/2+1, y-conStep['width']/2+1, x+conStep['width']/2, y+conStep['width']/2], fill=conStep['colour'])
                                
                            else:
                                offsetInfo = mathtools.dashOffset(preConCoords, conStep['dash'][0], conStep['dash'][1])[index:]
                                #print(offsetInfo)
                                for c in range(len(conCoords)-1):
                                    #print(offsetInfo)
                                    #print(c)
                                    o, emptyStart = offsetInfo[c]
                                    for dashCoords in mathtools.dash(conCoords[c][0], conCoords[c][1], conCoords[c+1][0], conCoords[c+1][1], conStep['dash'][0], conStep['dash'][1], o, emptyStart):
                                        #print(dashCoords)
                                        img.line(dashCoords, fill=conStep['colour'], width=conStep['width'])
                            internal.log(f"{tilePlas}: Segment drawn", 2, verbosityLevel)
                    operated += 1
                    timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
                    internal.log(f"Rendered road studs ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel)

        textList += pointsTextList 
        textList.reverse()
        dontCross = []
        #print(textList)
        for i, x, y, w, h, rot in textList:
            r = lambda a,b : mathtools.rotateAroundPivot(a, b, x, y, rot)
            currentBoxCoords = [r(x-w/2, y-h/2), r(x-w/2, y+h/2), r(x+w/2, y+h/2), r(x+w/2, y-h/2), r(x-w/2, y-h/2)]
            canPrint = True
            for box in dontCross:
                useless1, ox, oy, ow, oh, useless2 = textList[dontCross.index(box)]
                oMaxDist = ((ow/2)**2+(oh/2)**2)**0.5/2
                thisMaxDist = ((w/2)**2+(h/2)**2)**0.5/2
                dist = ((x-ox)**2+(y-oy)**2)**0.5
                if dist > oMaxDist + thisMaxDist:
                    continue
                for c in range(len(box)-1):
                    for d in range(len(currentBoxCoords)-1):
                        canPrint = False if mathtools.linesIntersect(box[c][0], box[c][1], box[c+1][0], box[c+1][1], currentBoxCoords[d][0], currentBoxCoords[d][1], currentBoxCoords[d+1][0], currentBoxCoords[d+1][1]) else canPrint
                        if not canPrint:
                            break
                    if not canPrint:
                        break
                if canPrint and mathtools.pointInPoly(currentBoxCoords[0][0], currentBoxCoords[0][1], box) or mathtools.pointInPoly(box[0][0], box[0][1], currentBoxCoords):
                    canPrint = False
                if canPrint == False:
                    break
            if canPrint:
                im.paste(i, (int(x-i.width/2), int(y-i.height/2)), i)
                internal.log(f"{tilePlas}: Text pasted", 2, verbosityLevel)
            else:
                internal.log(f"{tilePlas}: Text skipped", 2, verbosityLevel)
            dontCross.append(currentBoxCoords)
        operated += 1
        timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
        internal.log(f"Rendered text ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel)
        
        tileReturn[tilePlas] = im
        if saveImages:
            im.save(f'{saveDir}{tilePlas}.png', 'PNG')

        if operated != 0:
            timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
            internal.log(f"Rendered {tilePlas} ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 0, verbosityLevel)
        else:
            internal.log(f"Rendered {tilePlas}", 0, verbosityLevel)

    internal.log("Render complete", 0, verbosityLevel)

    return tileReturn