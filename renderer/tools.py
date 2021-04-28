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
import multiprocessing
import tqdm
import sys

import renderer.internal
import renderer.utils
import renderer.mathtools
init()

def plaJsonToTiles(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int):
    xMax, xMin, yMax, yMin = plaJson_findEnds(plaList, nodeList)
    return lineToTiles([(xMax,yMax),(xMin,yMax),(xMax,yMin),(xMin,yMin)], minZoom, maxZoom, maxZoomRange)

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
        coords = nodesToCoords(plaList[pla]['nodes'], nodeList)
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
        coords = nodesToCoords(plaList[pla]['nodes'], nodeList)
        tiles.extend(lineToTiles(coords, minZoom, maxZoom, maxZoomRange))

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
            tiles.extend(coordToTiles([x,y], minZoom, maxZoom, maxZoomRange))
    tiles = list(dict.fromkeys(tiles))
    return tiles