import math
from PIL import Image, ImageDraw, ImageFont
from typing import Union
import time
import glob
import re
import multiprocessing
import sys
import blessed
import os

import renderer.internals.internal as internal # type: ignore
import renderer.tools as tools
import renderer.validate as validate
import renderer.mathtools as mathtools
import renderer.internals.rendering as rendering # type: ignore
import renderer.misc as misc

def tileMerge(images: Union[str, dict], saveImages=True, saveDir="tiles/", zoom=[]):
    """
    Merges tiles rendered by renderer.render().
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#tileMerge
    """
    term = blessed.Terminal()
    imageDict = {}
    tileReturn = {}
    if isinstance(images, str):
        print(term.green("Retrieving images..."), end="\r")
        for d in glob.glob(glob.escape(images)+"*.png"):
            regex = re.search("^"+re.escape(images)+r"(-?\d+, -?\d+, -?\d+)\.png$", d) # pylint: disable=anomalous-backslash-in-string
            if regex == None:
                continue
            coord = regex.group(1)
            i = Image.open(d)
            imageDict[coord] = i
            with term.location(): print(term.green("Retrieving images... ") + f"Retrieved {coord}", end=term.clear_eos+"\r")
    else:
        imageDict = images
    print(term.green("\nAll images retrieved"))
    print(term.green("Determined zoom levels..."), end=" ")
    if zoom == []:
        for c in imageDict.keys():
            z = internal.strToTuple(c)[0]
            if not z in zoom:
                zoom.append(z)
    print(term.green("determined"))
    for z in zoom:
        print(term.green(f"Zoom {z}: ") + "Determining tiles to be merged", end=term.clear_eos+"\r")
        toMerge = {}
        for c, i in imageDict.items():
            #i = imageDict[c]
            if internal.strToTuple(c)[0] == z:
                toMerge[c] = i

        tileCoords = [internal.strToTuple(s) for s in toMerge.keys()]
        #print(tileCoords)
        xMax, xMin, yMax, yMin = tools.tile.findEnds(tileCoords)
        #print(imageDict.values())
        tileSize = list(imageDict.values())[0].size[0]
        i = Image.new('RGBA', (tileSize*(xMax-xMin+1), tileSize*(yMax-yMin+1)), (0, 0, 0, 0))
        px = 0
        py = 0
        merged = 0
        start = time.time() * 1000
        for x in range(xMin, xMax+1):
            for y in range(yMin, yMax+1):
                if f"{z}, {x}, {y}" in toMerge.keys():
                    i.paste(toMerge[f"{z}, {x}, {y}"], (px, py))
                    merged += 1
                    with term.location(): print(term.green(f"Zoom {z}: ") + f"{internal.percentage(merged, len(toMerge.keys()))} | {internal.msToTime(internal.timeRemaining(start, merged, len(toMerge.keys())))} left | " + term.bright_black(f"Pasted {z}, {x}, {y}"), end=term.clear_eos+"\r")
                py += tileSize
            px += tileSize
            py = 0
        #tileReturn[tilePlas] = im
        if saveImages:
            print(term.green(f"Zoom {z}: ") + "Saving image", end=term.clear_eos+"\r")
            i.save(f'{saveDir}merge_{z}.png', 'PNG')
        tileReturn[str(z)] = i
        
    print(term.green("\nAll merges complete"))
    return tileReturn

def render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: Union[str, float], saveImages=True, saveDir="", assetsDir=os.path.dirname(__file__)+"/skins/assets/", processes=1, tiles=None):
    """
    Renders tiles from given coordinates and zoom values.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.render
    """
    if maxZoom < minZoom:
        raise ValueError("Max zoom value is greater than min zoom value")
    term = blessed.Terminal()

    # validation
    print(term.green("Validating skin..."), end=" ")
    validate.vSkinJson(skinJson)
    print(term.green("validated\nValidating PLAs..."), end=" ")
    validate.vPlaJson(plaList, nodeList)
    print(term.green("validated\nValidating nodes..."), end=" ")
    validate.vNodeJson(nodeList)

    print(term.green("validated\nFinding tiles..."), end=" ")
    #finds which tiles to render
    if tiles != None:
        validate.vTileCoords(tiles, minZoom, maxZoom)
    else: #finds box of tiles
        tiles = tools.plaJson.renderedIn(plaList, nodeList, minZoom, maxZoom, maxZoomRange)

    print(term.green("found\nRemoving PLAs with unknown type..."), end=" ")
    # remove PLAs whose type is not in skin
    removeList = []
    for pla in plaList.keys():
        if not plaList[pla]['type'].split(' ')[0] in skinJson['order']:
            removeList.append(pla)
    for pla in removeList:
        del plaList[pla]
    print(term.green("removed"))
    if removeList != []:
        print(term.yellow('The following PLAs were removed:'))
        print(term.yellow(" | ".join(removeList)))

    print(term.green("Sorting PLA by tiles..."), end=" ")
    #sort PLAs by tiles
    tileList = {}
    for tile in tiles:
        tileList[internal.tupleToStr(tile)] = {}
    for pla in plaList.keys():
        coords = tools.nodes.toCoords(plaList[pla]['nodes'], nodeList)
        renderedIn = tools.line.toTiles(coords, minZoom, maxZoom, maxZoomRange)
        for tile in renderedIn:
            if internal.tupleToStr(tile) in tileList.keys():
                tileList[internal.tupleToStr(tile)][pla] = plaList[pla]
    
    processStart = time.time() * 1000
    processed = 0
    timeLeft = 0.0
    l = lambda processed, timeLeft, tilePlas, msg: term.green(f"{internal.percentage(processed, len(tileList))}% | {internal.msToTime(timeLeft)} left | ") + f"{tilePlas}: " + term.bright_black(msg) + term.clear_eos
    print(term.green("sorted\n")+term.bright_green("Starting processing"))
    for tilePlas in tileList.keys():
        #sort PLAs in tiles by layer
        newTilePlas = {}
        for pla in tileList[tilePlas].keys():
            if not str(float(tileList[tilePlas][pla]['layer'])) in newTilePlas.keys():
                newTilePlas[str(float(tileList[tilePlas][pla]['layer']))] = {}
            newTilePlas[str(float(tileList[tilePlas][pla]['layer']))][pla] = tileList[tilePlas][pla]
        with term.location(): print(l(processed, timeLeft, tilePlas, "Sorted PLA by layer"), end="\r")
        

        #sort PLAs in layers in files by type
        for layer in newTilePlas.keys():
            #print(newTilePlas[layer].items())
            newTilePlas[layer] = {k: v for k, v in sorted(newTilePlas[layer].items(), key=lambda x: skinJson['order'].index(x[1]['type'].split(' ')[0]))}
        with term.location(): print(l(processed, timeLeft, tilePlas, "Sorted PLA by type"), end="\r")
        
        #merge layers
        tileList[tilePlas] = {}
        layers = sorted(newTilePlas.keys(), key=lambda x: float(x))
        for layer in layers:
            for key, pla in newTilePlas[layer].items():
                tileList[tilePlas][key] = pla
        with term.location(): print(l(processed, timeLeft, tilePlas, "Merged layers"), end="\r")

        #groups PLAs of the same type if "road" tag present
        newerTilePlas = [{}]
        keys = list(tileList[tilePlas].keys())
        for i in range(len(tileList[tilePlas])):
            newerTilePlas[-1][keys[i]] = tileList[tilePlas][keys[i]]
            if i != len(keys)-1 and (tileList[tilePlas][keys[i+1]]['type'].split(' ')[0] != tileList[tilePlas][keys[i]]['type'].split(' ')[0] or not "road" in skinJson['types'][tileList[tilePlas][keys[i]]['type'].split(' ')[0]]['tags']):
                newerTilePlas.append({})
        tileList[tilePlas] = newerTilePlas
        with term.location(): print(l(processed, timeLeft, tilePlas, "PLAs grouped"), end="\r")

        processed += 1
        timeLeft = internal.timeRemaining(processStart, processed, len(tileList))
        #timeLeft = round(((int(round(time.time() * 1000)) - processStart) / processed * (len(tileList) - processed)), 2)
    
    print(term.green("100.00% | 0.0s left | ") + "Processing complete" + term.clear_eos)

    #count # of rendering operations
    print(term.bright_green("Counting no. of operations"))
    operations = 0
    opTiles = {}
    tileOperations = 0
    for tilePlas in tileList.keys():
        if tileList[tilePlas] == [{}]:
            opTiles[tilePlas] = 0
            continue

        for group in tileList[tilePlas]:
            info = skinJson['types'][list(group.values())[0]['type'].split(" ")[0]]
            style = []
            for zoom in info['style'].keys():
                if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tilePlas)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                    style = info['style'][zoom]
                    break
            for step in style:
                for _, pla in group.items():
                    operations += 1; tileOperations += 1
                if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                    operations += 1; tileOperations += 1
        operations += 1; tileOperations += 1 #text

        opTiles[tilePlas] = tileOperations
        tileOperations = 0
        print(f"Counted {tilePlas}", end=term.clear_eos+"\r")
    
    #render
    renderStart = time.time() * 1000
    print(term.bright_green("\nStarting render"))
    if __name__ == 'renderer.base':
        m = multiprocessing.Manager()
        operated = m.Value('i', 0)
        lock = m.Lock() # pylint: disable=no-member

        input = []
        for i in tileList.keys():
            input.append((lock, operated, renderStart, i, tileList[i], operations, plaList, nodeList, skinJson, minZoom, maxZoom, maxZoomRange, saveImages, saveDir, assetsDir))
        p = multiprocessing.Pool(processes)
        try:
            preresult = p.map(rendering.tiles, input)
        except KeyboardInterrupt:
            p.terminate()
            sys.exit()
        result = {}
        for i in preresult:
            if i == None:
                continue
            k, v = list(i.items())[0]
            result[k] = v

        print(term.green("100.00% | 0.0s left | ") + "Rendering complete" + term.clear_eos)
    print(term.bright_green("Render complete"))
    return result