from colorama import Fore, Style, init
import math
import json
from PIL import Image, ImageDraw
import os
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

class tools:
    def nodesToCoords(nodes: list, nodeList: dict):
        coords = []
        for nodeid in nodes:
            if not nodeid in nodeList.keys():
                raise KeyError(f"Node '{nodeid}' does not exist")
            coords.append((nodeList[nodeid]['x'],nodeList[nodeid]['y']))
        return coords
    
    def plaJson_findEnds(plaList: dict, nodeList: dict):
        xMax = 0
        xMin = 0
        yMax = 0
        yMin = 0
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
        xMax = 0
        xMin = 0
        yMax = 0
        yMin = 0
        for x, y in coords:
            xMax = x+10 if x > xMax else xMax
            xMin = x-10 if x < xMin else xMin
            yMax = y+10 if y > yMax else yMax
            yMin = y-10 if y < yMin else yMin
        for x in range(xMin, xMax+1):
            for y in range(yMin, yMax+1):
                tiles.extend(tools.coordToTiles([x,y], minZoom, maxZoom, maxZoomRange))
        tiles = list(dict.fromkeys(tiles))
        return tiles


def render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, **kwargs):
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
        for layer in newTilePlas.values():
            for key, pla in layer.items():
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

        print(Fore.GREEN + "Processed " + tilePlas + Style.RESET_ALL)

    #print(tileList)
            
    print(Fore.GREEN + "Starting render..." + Style.RESET_ALL)
    for tilePlas in tileList.keys():
        if tileList[tilePlas] == [{}]:
            continue
        
        size = maxZoomRange*2**(maxZoom-internal.strToTuple(tilePlas)[0])
        im = Image.new(mode = "RGB", size = (1024, 1024), color = (238, 238, 238))
        img = ImageDraw.Draw(im)
        #im.save(f'tiles/{tilePlas}.png', 'PNG')
        for group in tileList[tilePlas]:
            info = skinJson['types'][list(group.values())[0]['type']]
            style = []
            for zoom in info['style'].keys():
                if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tilePlas)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                    style = info['style'][zoom]
                    break
            for step in style:
                for plaId, pla in group.items():
                    coords = [(x-internal.strToTuple(tilePlas)[1]*size, y-internal.strToTuple(tilePlas)[2]*size) for x,y in tools.nodesToCoords(pla['nodes'], nodeList)]
                    coords = [(int(1024/maxZoomRange*x), int(1024/maxZoomRange*y)) for x,y in coords]
                    #print(step)
                    if info["type"] == "line":
                        img.line(coords, fill=step['colour'], width=step['width'])
                        for x, y in coords:
                            img.ellipse([x-step['width']/2+1, y-step['width']/2+1, x+step['width']/2, y+step['width']/2], fill=step['colour'])
                    elif info['type'] == "area":
                        img.polygon(coords, fill=step['colour'])
        
        if not os.path.isdir('./tiles'):
            os.mkdir(os.getcwd()+"tiles")
        im.save(f'tiles/{tilePlas}.png', 'PNG')
        print(Fore.GREEN + "Rendered " + tilePlas + Style.RESET_ALL)
