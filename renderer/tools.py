import math

import renderer.internal as internal
import renderer.validate as validate
import renderer.mathtools as mathtools
import renderer.rendering as rendering
import renderer.misc as misc

class plaJson:
    @staticmethod
    def toTiles(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int):
        """
        Finds all the tiles that all the PLAs in the JSON will be rendered in.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.plaJson.toTiles
        """
        xMax, xMin, yMax, yMin = plaJson.findEnds(plaList, nodeList)
        return line.toTiles([(xMax,yMax),(xMin,yMax),(xMax,yMin),(xMin,yMin)], minZoom, maxZoom, maxZoomRange)
    
    @staticmethod
    def findEnds(plaList: dict, nodeList: dict):
        """
        Finds the minimum and maximum X and Y values of a JSON or dictionary of PLAs
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.plaJson.findEnds
        """
        xMax = -math.inf
        xMin = math.inf
        yMax = -math.inf
        yMin = math.inf
        for pla in plaList.keys():
            coords = nodes.toCoords(plaList[pla]['nodes'], nodeList)
            for x, y in coords:
                xMax = x if x > xMax else xMax
                xMin = x if x < xMin else xMin
                yMax = y if y > yMax else yMax
                yMin = y if y < yMin else yMin
        return xMax, xMin, yMax, yMin

    @staticmethod
    def renderedIn(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int):
        """
        Like renderer.tools.lineToTiles(), but for a JSON or dictionary of PLAs.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.plaJson.renderedIn
        """
        if maxZoom < minZoom:
            raise ValueError("Max zoom value is lesser than min zoom value")

        tiles = []
        for pla in plaList.keys():
            coords = nodes.toCoords(plaList[pla]['nodes'], nodeList)
            tiles.extend(line.toTiles(coords, minZoom, maxZoom, maxZoomRange))

        return tiles

class tile:
    @staticmethod
    def findEnds(coords: list):
        """
        Find the minimum and maximum x/y values of a set of tiles coords.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.tile.findEnds
        """
        xMax = -math.inf
        xMin = math.inf
        yMax = -math.inf
        yMin = math.inf
        for _, x, y in coords:
            xMax = x if x > xMax else xMax
            xMin = x if x < xMin else xMin
            yMax = y if y > yMax else yMax
            yMin = y if y < yMin else yMin
        return xMax, xMin, yMax, yMin

class line:
    @staticmethod
    def findEnds(coords: list):
        """
        Find the minimum and maximum x/y values of a set of coords.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.line.findEnds
        """
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

    @staticmethod
    def toTiles(coords: list, minZoom: int, maxZoom: int, maxZoomRange: int):
        """
        Generates tile coordinates from list of regular coordinates using renderer.tools.coordToTiles().
        More info: Mainly for rendering whole PLAs. https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.line.toTiles
        """
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
                tiles.extend(coord.toTiles([x,y], minZoom, maxZoom, maxZoomRange))
        tiles = list(dict.fromkeys(tiles))
        return tiles

class nodes:
    @staticmethod
    def findPlasAttached(nodeId: str, plaList: dict):
        """
        Finds which PLAs attach to a node.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.nodes.findPlasAttached
        """
        plas = []
        for plaId, pla in plaList.items():
            #print(plaId)
            if nodeId in pla['nodes']:
                plas.append((plaId, pla['nodes'].index(nodeId)))
        return plas

    @staticmethod
    def toCoords(nodes: list, nodeList: dict):
        """
        Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.nodes.toCoords
        """
        coords = []
        for nodeid in nodes:
            if not nodeid in nodeList.keys():
                raise KeyError(f"Node '{nodeid}' does not exist")
            coords.append((nodeList[nodeid]['x'],nodeList[nodeid]['y']))
        return coords

class coord:
    @staticmethod
    def toTiles(coord: list, minZoom: int, maxZoom: int, maxZoomRange: int):
        """
        Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.
        More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.tools.coord.toTiles
        """
        if maxZoom < minZoom:
            raise ValueError("Max zoom value is lesser than min zoom value")

        tiles = []
        for z in reversed(range(minZoom, maxZoom+1)):
            x = math.floor(coord[0] / maxZoomRange)
            y = math.floor(coord[1] / maxZoomRange)
            tiles.append((z,x,y))
            maxZoomRange *= 2

        return tiles