from colorama import Fore, Style, init
import math
import json
from PIL import Image, ImageDraw, ImageFont
import os
import sympy as sym
from typing import Union
import time
init()

class utils:
    def coordListIntegrity(coords: list, **kwargs):
        doError = True if 'error' in kwargs.keys() and kwargs['error'] == True else False
        silent = True if 'silent' in kwargs.keys() and kwargs['silent'] == True else False
        def throwError(msg, error):
            if doError:
                print(Fore.RED, end="")
                raise error(msg)
            else:
                print(Fore.RED + msg + Style.RESET_ALL)
                return msg

        if not silent:
            print(Fore.GREEN + "Starting coordinates list check..." + Style.RESET_ALL)
        errors = []
        for coord in coords:
            if not isinstance(coord, tuple):
                errors.append(throwError(f"Coord '{str(coord)}' is type {str(type(coord).__name__)} instead of tuple", TypeError))
            elif len(coord) != 2:
                errors.append(throwError(f"Coord '{str(coord)}' has {str(len(coord))} values instead of 2", ValueError))
            else:
                for n in coord:
                    if not isinstance(n, (int, float)):
                        errors.append(throwError(f"Coord '{str(coord)}' has '{str(n)}' which is not int/float", ValueError))
        if not silent:
            print(Fore.GREEN + "Check complete; below is a list of errors if any:" + Style.RESET_ALL)
            if errors == []:
                errors = ["None"]
            print("\n".join(errors))
        return errors

    def tileCoordListIntegrity(tiles: list, minZoom: int, maxZoom: int, **kwargs):
        if maxZoom < minZoom:
            raise ValueError("Max zoom value is lesser than min zoom value")

        doError = True if 'error' in kwargs.keys() and kwargs['error'] == True else False
        silent = True if 'silent' in kwargs.keys() and kwargs['silent'] == True else False
        def throwError(msg, error):
            if doError:
                print(Fore.RED, end="")
                raise error(msg)
            else:
                print(Fore.RED + msg + Style.RESET_ALL)
                return msg

        if not silent:
            print(Fore.GREEN + "Starting tile coordinates list check..." + Style.RESET_ALL)
        errors = []
        for coord in tiles:
            if not isinstance(coord, tuple):
                errors.append(throwError(f"Tile '{str(coord)}' is type {str(type(coord).__name__)} instead of tuple", TypeError))
            elif len(coord) != 3:
                errors.append(throwError(f"Tile '{str(coord)}' has {str(len(coord))} values instead of 3", ValueError))
            else:
                for n in coord:
                    if not isinstance(n, (int, float)):
                        errors.append(throwError(f"Tile '{str(coord)}' has '{str(n)}' which is not int/float", ValueError))
                if coord[0] < minZoom or coord[0] > maxZoom:
                    errors.append(throwError(f"Zoom of tile '{str(coord)}' is {str(coord[0])} which is out of zoom range {str(minZoom)} - {str(maxZoom)}", ValueError))
        if not silent:
            print(Fore.GREEN + "Check complete; below is a list of errors if any:" + Style.RESET_ALL)
            if errors == []:
                errors = ["None"]
            print("\n".join(errors))
        return errors
        
    def nodeJsonIntegrity(nodeList: dict, **kwargs):
        doError = True if 'error' in kwargs.keys() and kwargs['error'] == True else False
        def throwError(msg, error):
            if doError:
                print(Fore.RED, end="")
                raise error(msg)
            else:
                print(Fore.RED + msg + Style.RESET_ALL)
                return msg

        print(Fore.GREEN + "Starting Node JSON integrity check..." + Style.RESET_ALL)
        errors = []
        for node in nodeList.keys():
            print(Fore.GREEN + f"{node}: Starting check" + Style.RESET_ALL)
            for key in ["x","y","connections"]:
                if not key in nodeList[node].keys():
                    errors.append(throwError(f"{node}: Key '{key}' missing", KeyError))

            for key in nodeList[node].keys():
                if key in ["x", "y"] and not isinstance(nodeList[node][key], (int, float)):
                    errors.append(throwError(f"{node}: Value of key '{key}' is type {str(type(nodeList[node][key]).__name__)} instead of int/float", TypeError))
        print(Fore.GREEN + "Checks complete; below is a list of errors if any:" + Style.RESET_ALL)
        if errors == []:
            errors = ["None"]
        print("\n".join(errors))
        return errors

    def nodeListIntegrity(nodes: list, nodeList: dict, **kwargs):
        doError = True if 'error' in kwargs.keys() and kwargs['error'] == True else False
        silent = True if 'silent' in kwargs.keys() and kwargs['silent'] == True else False
        def throwError(msg, error):
            if doError:
                print(Fore.RED, end="")
                raise error(msg)
            else:
                print(Fore.RED + msg + Style.RESET_ALL)
                return msg

        if not silent:
            print(Fore.GREEN + "Starting node list check..." + Style.RESET_ALL)
        errors = []
        for node in nodes:
            if not node in nodeList.keys():
                errors.append(throwError(f"Node '{node}' does not exist", ValueError))
        if not silent:
            print(Fore.GREEN + "Check complete; below is a list of errors if any:" + Style.RESET_ALL)
            if errors == []:
                errors = ["None"]
            print("\n".join(errors))
        return errors

    def plaJsonIntegrity(plaList: dict, nodeList: dict, **kwargs):
        doError = True if 'error' in kwargs.keys() and kwargs['error'] == True else False
        def throwError(msg, error):
            if doError:
                print(Fore.RED, end="")
                raise error(msg)
            else:
                print(Fore.RED + msg + Style.RESET_ALL)
                return msg

        print(Fore.GREEN + "Starting PLA JSON integrity check..." + Style.RESET_ALL)
        errors = []
        for pla in plaList.keys():
            print(Fore.GREEN + f"{pla}: Starting check" + Style.RESET_ALL)
            for key in ["type","displayname","description","layer","nodes","attrs"]:
                if not key in plaList[pla].keys():
                    errors.append(throwError(f"{pla}: Key '{key}' missing", KeyError))

            for key in plaList[pla].keys():
                if key in ["type", "displayname", "description"] and not isinstance(plaList[pla][key], str):
                    errors.append(throwError(f"{pla}: Value of key '{key}' is type {str(type(plaList[pla][key]).__name__)} instead of str", TypeError))
                elif key in ["layer"] and not isinstance(plaList[pla][key], (int, float)):
                    errors.append(throwError(f"{pla}: Value of key '{key}' is type {str(type(plaList[pla][key]).__name__)} instead of int/float", TypeError))
                elif key in ["nodes"]:
                    if not isinstance(plaList[pla][key], list):
                        errors.append(throwError(f"{pla}: Value of key '{key}' is type {str(type(plaList[pla][key]).__name__)} instead of list", TypeError))
                    elif key == "nodes":
                        temp = utils.nodeListIntegrity(plaList[pla][key], nodeList, error=doError, silent=True)
                        for e in temp:
                            errors.append(f"{pla}: " + e)
                elif key in ["attr"]:
                    if not isinstance(plaList[pla][key], dict):
                        errors.append(throwError(f"{pla}: Value of key '{key}' is type {str(type(plaList[pla][key]).__name__)} instead of dict", TypeError))

                #if key == "shape" and not plaList[pla][key] in ["point", "line", "area"]:
                    #errors.append(throwError(f"{pla}: Shape is '{plaList[pla][key]}' instead of PLA type", ValueError))
        print(Fore.GREEN + "Checks complete; below is a list of errors if any:" + Style.RESET_ALL)
        if errors == []:
            errors = ["None"]
        print("\n".join(errors))
        return errors
                
class internal:
    def dictIndex(d: dict, v):
        return list(d.keys())[list(d.values()).index(v)]

    def readJson(file: str):
        with open(file, "r") as f:
            data = json.load(f)
            f.close()
            return data

    def writeJson(file: str, data: dict, **kwargs):
        pp = True if 'pp' in kwargs.keys() and kwargs['pp'] == True else False
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

    def msToTime(ms):
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
        points = []
        for p in range(1, n+1):
            x3, y3 = (x1+p*(x2-x1)/(n+1),y1+p*(y2-y1)/(n+1))
            #x3, y3 = ((x1+x2)/2, (y1+y2)/2)
            xv, yv = sym.symbols('xv,yv')
            if x1 == x2:
                m1 = None
                m2 = 0
                eq1 = sym.Eq(yv,y3)
            elif y1 == y2:
                m1 = 0
                m2 = None
                eq1 = sym.Eq(xv,x3)
            else:
                m1 = (y2-y1)/(x2-x1)
                m2 = -1 / m1
                eq1 = sym.Eq(yv-y3,m2*(xv-x3))
            eq2 = sym.Eq(((yv-y3)**2 + (xv-x3)**2)**0.5,abs(o))
            results = sym.solve([eq1, eq2], (xv, yv)) if o != 0 else [(x3, y3), (x3, y3)]
            if returnBoth:
                rot = 90 if x1 == x2 else math.degrees(-math.atan(m1))
                points += [(results[0][0], results[0][1], rot), (results[1][0], results[1][1], rot)]
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
        if isinstance(result, list):
            x5, y5 = result[0]
        elif isinstance(result, dict):
            x5 = result[xv]
            y5 = result[yv]
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

    def lineInBox(line: list, top: int, bottom: int, left: int, right: int):
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

    def dash(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], d: Union[int, float]):
        if d <= 0:
            return None
        xv, yv = sym.symbols('xv,yv')
        if x1 == x2:
            m = None
            eq1 = sym.Eq(xv,x1)
        else:
            m = (y2-y1)/(x2-x1)
            eq1 = sym.Eq(yv-y1,m*(xv-x1))
        eq2 = sym.Eq(((yv-y1)**2 + (xv-x1)**2)**0.5,d)
        results = sym.solve([eq1, eq2], (xv, yv))
        x3, y3 = results[0] if min(x1,x2) <= results[0][0] <= max(x1,x2) and min(y1,y2) <= results[0][1] <= max(y1,y2) else results[1]
        dx, dy = (x3-x1, y3-y1)
        predash = [(x1, y1), (x3, y3)]
        while x2-x3 >= dx and y2-y3 >= dy:
            x3 += dx; y3 += dy
            predash.append((x3, y3))
        predash[-1] = (round(predash[-1][0], 12), round(predash[-1][1], 12))
        if predash[-1] != (x2, y2):
            predash.append((x2, y2))
        dash = []
        for coord in predash:
            if predash.index(coord) % 2 == 0:
                dash.append([coord])
            else:
                dash[-1].append(coord)
        if len(dash[-1]) == 1:
            dash.pop()
        return dash
   
class tools:
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
        for x in range(xMin, xMax+1, int(maxZoomRange/2)):
            for y in range(yMin, yMax+1, int(maxZoomRange/2)):
                tiles.extend(tools.coordToTiles([x,y], minZoom, maxZoom, maxZoomRange))
        tiles = list(dict.fromkeys(tiles))
        return tiles


def render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, assetsDir="skins/assets/", **kwargs):
    if maxZoom < minZoom:
        raise ValueError("Max zoom value is greater than min zoom value")

    # integrity checks
    utils.plaJsonIntegrity(plaList, nodeList, error=True)
    utils.nodeJsonIntegrity(nodeList, error=True)

    #finds which tiles to render
    if 'tiles' in kwargs.keys() and isinstance(kwargs['tiles'], list):
        tiles = kwargs['tiles']
        utils.tileCoordListIntegrity(tiles, minZoom, maxZoom, error=True)
    else: #finds box of tiles
        xMax, xMin, yMax, yMin = tools.plaJson_findEnds(plaList, nodeList)
        tiles = tools.lineToTiles([(xMax,yMax),(xMin,yMax),(xMax,yMin),(xMin,yMin)], minZoom, maxZoom, maxZoomRange)

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
    
    #print(tileList)
    
    processStart = time.time() * 1000
    processed = 0
    print(Fore.GREEN + "Starting processing..." + Style.RESET_ALL)
    for tilePlas in tileList.keys():
        #sort PLAs in tiles by layer
        newTilePlas = {}
        for pla in tileList[tilePlas].keys():
            if not str(float(tileList[tilePlas][pla]['layer'])) in newTilePlas.keys():
                newTilePlas[str(float(tileList[tilePlas][pla]['layer']))] = {}
            newTilePlas[str(float(tileList[tilePlas][pla]['layer']))][pla] = tileList[tilePlas][pla]
    
        #sort PLAs in layers in files by type
        for layer in newTilePlas.keys():
            #print(newTilePlas[layer].items())
            newTilePlas[layer] = {k: v for k, v in sorted(newTilePlas[layer].items(), key=lambda x: skinJson['order'].index(x[1]['type'].split(' ')[0]))}
        
        #merge layers
        tileList[tilePlas] = {}
        layers = sorted(newTilePlas.keys(), key=lambda x: float(x))
        for layer in layers:
            for key, pla in newTilePlas[layer].items():
                tileList[tilePlas][key] = pla
        
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

        processed += 1
        timeLeft = round(((int(round(time.time() * 1000)) - processStart) / processed * (len(tileList) - processed)), 2)
        #logging.info('tile %d/%d [%d, %d] (%s left)', processed, len(tileList), x, y, msToTime(timeLeft))
        print(f"Processed {tilePlas} ({round(processed/len(tileList)*100, 2)}%, {internal.msToTime(timeLeft)} remaining)" + Style.RESET_ALL)
    
    #print(tileList)
    renderStart = time.time() * 1000
    rendered = 0
    print(Fore.GREEN + "Starting render..." + Style.RESET_ALL)
    for tilePlas in tileList.keys():
        if tileList[tilePlas] == [{}]:
            continue
        
        size = maxZoomRange*2**(maxZoom-internal.strToTuple(tilePlas)[0])
        im = Image.new(mode = "RGBA", size = (skinJson['info']['size'], skinJson['info']['size']), color = (221, 221, 221))
        img = ImageDraw.Draw(im)
        textList = []

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

                    if info['type'] == "point":
                        if step['shape'] == "circle":
                            img.ellipse([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2], fill=step['colour'], outline=step['outline'], width=step['width'])
                        elif step['shape'] == "text":
                            font = getFont("", step['size'])
                            img.text((coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1]), pla['displayname'], fill=step['colour'], font=font, anchor=step['anchor'])
                        elif step['shape'] == "square":
                            img.rectangle([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2], fill=step['colour'], outline=step['outline'], width=step['width'])
                        elif step['shape'] == "image":
                            icon = Image.open(assetsDir+step['file'])
                            im.paste(icon, (int(coords[0][0]-icon.width/2+step['offset'][0]), int(coords[0][1]-icon.height/2+step['offset'][1])), icon)

                    elif info['type'] == "line" and step['layer'] == "text":
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        for c in range(len(coords)-1):
                            #print(coords)
                            #print(mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']))
                            t = math.floor(((coords[c+1][0]-coords[c][0])**2+(coords[c+1][1]-coords[c][1])**2)**0.5/(4*textLength))
                            t = 1 if t == 0 else t
                            if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= ((coords[c+1][0]-coords[c][0])**2+(coords[c+1][1]-coords[c][1])**2)**0.5:
                                #print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset']))     
                                for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=t):
                                    i = Image.new('RGBA', (2*textLength,50), (0, 0, 0, 0))
                                    d = ImageDraw.Draw(i)
                                    d.text((textLength, 25), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                                    i = i.rotate(trot, expand=True)
                                    textList.append((i, tx, ty))
                            if "oneWay" in pla['type'].split(" ")[1:]:
                                font = ImageFont.truetype("skins/assets/ClearSans-Bold.ttf", step['size'])
                                counter = 0
                                for tx, ty, useless in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=2*t+1):
                                    if counter % 2 == 1:
                                        counter += 1
                                        continue
                                    trot = math.degrees(math.atan2(coords[c+1][0]-coords[c][0], coords[c+1][1]-coords[c][1]))
                                    i = Image.new('RGBA', (2*textLength,50), (0, 0, 0, 0))
                                    d = ImageDraw.Draw(i)
                                    d.text((textLength, 25), "↓", fill=step['colour'], font=font, anchor="mm")
                                    i = i.rotate(trot, expand=True)
                                    textList.append((i, tx, ty))
                                    counter += 1
                                
                    elif info['type'] == "line":
                        if not "dash" in step.keys():
                            img.line(coords, fill=step['colour'], width=step['width'])
                            for x, y in coords:
                                img.ellipse([x-step['width']/2+1, y-step['width']/2+1, x+step['width']/2, y+step['width']/2], fill=step['colour'])
                        else:
                            for c in range(len(coords)-1):
                                for dashCoords in mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['dash']):
                                    print(dashCoords)
                                    img.line(dashCoords, fill=step['colour'], width=step['width'])                

                    elif info['type'] == "area" and step['layer'] == "bordertext":
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        for c1 in range(len(coords)):
                            c2 = c1+1 if c1 != len(coords)-1 else 0
                            if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= ((coords[c2][0]-coords[c1][0])**2+(coords[c2][1]-coords[c1][1])**2)**0.5:
                                #coords[c]
                                t = math.floor(((coords[c2][0]-coords[c1][0])**2+(coords[c2][1]-coords[c1][1])**2)**0.5/(4*textLength))
                                t = 1 if t == 0 else t
                                allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1], step['offset'], n=t, returnBoth=True)
                                for n in range(0, len(allPoints), 2):
                                    points = [allPoints[n], allPoints[n+1]]
                                    if step['offset'] < 0:
                                        tx, ty, trot = points[0] if not mathtools.pointInPoly(points[0][0], points[0][1], coords) else points[1]
                                    else:
                                        #print(points[0][0], points[0][1], coords)
                                        #print(mathtools.pointInPoly(points[0][0], points[0][1], coords))
                                        tx, ty, trot = points[0] if mathtools.pointInPoly(points[0][0], points[0][1], coords) else points[1]
                                    i = Image.new('RGBA', (2*textLength,50), (0, 0, 0, 0))
                                    d = ImageDraw.Draw(i)
                                    d.text((textLength, 25), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                                    i = i.rotate(trot, expand=True)
                                    textList.append((i, tx, ty))

                    elif info['type'] == "area" and step['layer'] == "centertext":
                        cx, cy = mathtools.polyCenter(coords)
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        i = Image.new('RGBA', (2*textLength,50), (0, 0, 0, 0))
                        d = ImageDraw.Draw(i)
                        d.text((textLength, 25), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                        textList.append((i, cx, cy))
                                
                    elif info['type'] == "area":
                        img.polygon(coords, fill=step['colour'], outline=step['outline'])
                        
                    print(Style.DIM + f"Rendered step {style.index(step)+1} of {len(style)} of PLA {plaId}" + Style.RESET_ALL)

                if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                    nodes = []
                    for pla in group.values():
                        nodes += pla['nodes']
                    connectedPre = [tools.findPlasAttachedToNode(x, plaList) for x in nodes]
                    connected = []
                    for i in connectedPre:
                       connected += i
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
                    
                            if index == 0:
                                conCoords = [conCoords[0], conCoords[1]]
                                conCoords[1] = ((conCoords[0][0]+conCoords[1][0])/2, (conCoords[0][1]+conCoords[1][1])/2)
                            elif index == len(conCoords)-1:
                                conCoords = [conCoords[index-1], conCoords[index]]
                                conCoords[0] = ((conCoords[0][0]+conCoords[1][0])/2, (conCoords[0][1]+conCoords[1][1])/2)
                            else:
                                conCoords = [conCoords[index-1], conCoords[index], conCoords[index+1]]
                                conCoords[0] = ((conCoords[0][0]+conCoords[1][0])/2, (conCoords[0][1]+conCoords[1][1])/2)
                                conCoords[2] = ((conCoords[2][0]+conCoords[1][0])/2, (conCoords[2][1]+conCoords[1][1])/2)
                            if not "dash" in conStep.keys():
                                img.line(conCoords, fill=conStep['colour'], width=conStep['width'])
                                for x, y in conCoords:
                                    img.ellipse([x-conStep['width']/2+1, y-conStep['width']/2+1, x+conStep['width']/2, y+conStep['width']/2], fill=conStep['colour'])
                            else:
                                for c in range(len(conCoords)-1):
                                    for dashCoords in mathtools.dash(conCoords[c][0], conCoords[c][1], conCoords[c+1][0], conCoords[c+1][1], conStep['dash']):
                                        #print(dashCoords)
                                        img.line(dashCoords, fill=conStep['colour'], width=conStep['width'])
                    print(Style.DIM + "Rendered road studs" + Style.RESET_ALL)
                            
        for i, x, y in textList:
            im.paste(i, (int(x-i.width/2), int(y-i.height/2)), i)
        print(Style.DIM + "Rendered text" + Style.RESET_ALL)
        
        if not os.path.isdir('tiles'):
            os.mkdir(os.getcwd()+"/tiles")
        im.save(f'tiles/{tilePlas}.png', 'PNG')

        rendered += 1
        timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / rendered * (len(tileList) - rendered)), 2)
        print(Fore.GREEN + f"Rendered {tilePlas} ({round(rendered/len(tileList)*100, 2)}%, {internal.msToTime(timeLeft)} remaining)" + Style.RESET_ALL)
    
    print(Fore.GREEN + "Render complete" + Style.RESET_ALL)
