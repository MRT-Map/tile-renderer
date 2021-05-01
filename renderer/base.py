import math
from PIL import Image, ImageDraw, ImageFont
from typing import Union
import time
import glob
import re
import multiprocessing
import tqdm
import sys
import blessed

import renderer.internal as internal
import renderer.tools as tools
import renderer.validate as validate
import renderer.mathtools as mathtools
import renderer.rendering as rendering

def tileMerge(images: Union[str, dict], verbosityLevel=1, saveImages=True, saveDir="tiles/", zoom=[], logPrefix=""):
    """
    Merges tiles rendered by renderer.render().
    More info: https://tile-renderer.readthedocs.io/en/main/functions.html#tileMerge
    """
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
            internal.log(f"Retrieved {coord}", 1, verbosityLevel, logPrefix)
    else:
        imageDict = images
    internal.log("Retrieved all images", 0, verbosityLevel, logPrefix)
    
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
    internal.log("Zoom levels determined", 0, verbosityLevel, logPrefix)
    for z in range(minZoom, maxZoom+1):
        toMerge = {}
        for c, i in imageDict.items():
            #i = imageDict[c]
            if internal.strToTuple(c)[0] == z:
                toMerge[c] = i
                internal.log(f"Zoom {z} will include {c}", 1, verbosityLevel, logPrefix)
        internal.log(f"Zoom {z}: Tiles to be merged determined", 0, verbosityLevel, logPrefix)
        tileCoords = [internal.strToTuple(s) for s in toMerge.keys()]
        #print(tileCoords)
        xMax, xMin, yMax, yMin = tools.tile.findEnds(tileCoords)
        #print(imageDict.values())
        tileSize = list(imageDict.values())[0].size[0]
        i = Image.new('RGBA', (tileSize*(xMax-xMin+1), tileSize*(yMax-yMin+1)), (0, 0, 0, 0))
        px = 0
        py = 0
        for x in range(xMin, xMax+1):
            for y in range(yMin, yMax+1):
                if f"{z}, {x}, {y}" in toMerge.keys():
                    i.paste(toMerge[f"{z}, {x}, {y}"], (px, py))
                    internal.log(f"{z}, {x}, {y} pasted", 1, verbosityLevel, logPrefix)
                py += tileSize
            px += tileSize
            py = 0
        #tileReturn[tilePlas] = im
        if saveImages:
            i.save(f'{saveDir}merge_{z}.png', 'PNG')
        tileReturn[str(z)] = i
        internal.log(f"Zoom {z} merged", 0, verbosityLevel, logPrefix)
        
    internal.log("All merges complete", 0, verbosityLevel, logPrefix)
    return tileReturn

def render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, verbosityLevel=1, saveImages=True, saveDir="", assetsDir="renderer/skins/assets/", logPrefix="", tiles=None):
    """
    Renders tiles from given coordinates and zoom values.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.render
    """
    if maxZoom < minZoom:
        raise ValueError("Max zoom value is greater than min zoom value")
    #tileReturn = {}
    term = blessed.Terminal()

    # validation
    print(term.green("Validating skin..."), end=" ")
    #internal.log("Validating skin...", 0, verbosityLevel, logPrefix)
    validate.vSkinJson(skinJson)
    print(term.green("validated\nValidating PLAs..."), end=" ")
    #internal.log("Validating PLAs...", 0, verbosityLevel, logPrefix)
    validate.vPlaJson(plaList, nodeList)
    print(term.green("validated\nValidating nodes..."), end=" ")
    #internal.log("Validating nodes...", 0, verbosityLevel, logPrefix)
    validate.vNodeJson(nodeList)

    print(term.green("validated\nFinding tiles..."), end=" ")
    #finds which tiles to render
    if tiles != None:
        validate.vTileCoords(tiles, minZoom, maxZoom)
    else: #finds box of tiles
        tiles = tools.plaJson.toTiles(plaList, nodeList, minZoom, maxZoom, maxZoomRange)

    print(term.green("found\nSorting PLA by tiles..."), end=" ")
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
    #internal.log("Sorted PLA by tiles", 2, verbosityLevel, logPrefix)
    
    #print(tileList)
    
    processStart = time.time() * 1000
    processed = 0
    timeLeft = 0.0
    l = lambda processed, timeLeft, tilePlas, msg: term.clear_eol + term.green(f"{internal.percentage(processed, len(tileList))}% | {internal.msToTime(timeLeft)} left | ") + f"{tilePlas}: " + term.bright_black(msg)
    print(term.green("sorted\n")+term.bright_green("Starting processing"))
    for tilePlas in tileList.keys():
        #sort PLAs in tiles by layer
        newTilePlas = {}
        for pla in tileList[tilePlas].keys():
            if not str(float(tileList[tilePlas][pla]['layer'])) in newTilePlas.keys():
                newTilePlas[str(float(tileList[tilePlas][pla]['layer']))] = {}
            newTilePlas[str(float(tileList[tilePlas][pla]['layer']))][pla] = tileList[tilePlas][pla]
        #internal.log(f"{tilePlas}: Sorted PLA by layer", 2, verbosityLevel, logPrefix)
        print(l(processed, timeLeft, tilePlas, "Sorted PLA by layer"), end="\r")
        

        #sort PLAs in layers in files by type
        for layer in newTilePlas.keys():
            #print(newTilePlas[layer].items())
            newTilePlas[layer] = {k: v for k, v in sorted(newTilePlas[layer].items(), key=lambda x: skinJson['order'].index(x[1]['type'].split(' ')[0]))}
        #internal.log(f"{tilePlas}: Sorted PLA by type", 2, verbosityLevel, logPrefix)
        print(l(processed, timeLeft, tilePlas, "Sorted PLA by type"), end="\r")
        
        #merge layers
        tileList[tilePlas] = {}
        layers = sorted(newTilePlas.keys(), key=lambda x: float(x))
        for layer in layers:
            for key, pla in newTilePlas[layer].items():
                tileList[tilePlas][key] = pla
        #internal.log(f"{tilePlas}: Merged layers", 2, verbosityLevel, logPrefix)
        print(l(processed, timeLeft, tilePlas, "Merged layers"), end="\r")
        
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
        #internal.log("PLAs grouped", 2, verbosityLevel, logPrefix)
        print(l(processed, timeLeft, tilePlas, "PLAs grouped"), end="\r")

        processed += 1
        timeLeft = internal.timeRemaining(processStart, processed, len(tileList))
        #timeLeft = round(((int(round(time.time() * 1000)) - processStart) / processed * (len(tileList) - processed)), 2)
        #internal.log(f"Processed {tilePlas} ({round(processed/len(tileList)*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)
    print(term.bright_green("\nCounting no. of operations"))
    #count # of rendering operations
    #internal.log("Counting no. of operations", 0, verbosityLevel, logPrefix)
    
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
        print(term.clear_eol + f"Counted {tilePlas}", end="\r")
    
    #render
    processes=10
    #operated = 0
    renderStart = time.time() * 1000
    print(term.bright_green("\nStarting render..."))
    if processes > 0 and __name__ == 'renderer.base':
        operated = multiprocessing.Manager().Value('i', 0)

        #print(term.bright_green(f"{internal.percentage(operated, operations)}% | 0.0s left"))
        #for n in range(processes):
        #    print(term.bright_green(f"{n+1} | ")+term.green(f"00.0% | 0.0s left |"))

        input = []
        for i in tileList.keys():
            #print(type(tileList[i]))
            input.append((operated, renderStart, i, tileList[i], operations, plaList, nodeList, skinJson, minZoom, maxZoom, maxZoomRange, verbosityLevel, saveImages, saveDir, assetsDir, logPrefix, processes))
            #print(len(tileList[i]))
        p = multiprocessing.Pool(5)
        try:
            #internal.writeJson("a.json", {"a":input}, True)
            #print(len(tileList.values()))
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
    else:
        pass

    print(term.bright_green("\nRender complete"))
    
    #return tileReturn
    return result