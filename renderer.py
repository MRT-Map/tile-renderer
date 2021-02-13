import rich
import math

class tools:
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
            xMax = x if x > xMax else xMax
            xMin = x if x < xMin else xMin
            yMax = y if y > yMax else yMax
            yMin = y if y < yMin else yMin
        for x in range(xMin, xMax+1):
            for y in range(yMin, yMax+1):
                tiles.extend(tools.coordToTiles([x,y], minZoom, maxZoom, maxZoomRange))
        tiles = list(dict.fromkeys(tiles))
        return tiles
    

def render(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int, **kwargs):
    if maxZoom < minZoom:
        raise ValueError("Max zoom value is greater than min zoom value")

    tiles = kwargs['tiles'] if 'tiles' in kwargs.keys() else None # array of (z,x,y)