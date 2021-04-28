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

import renderer.internal as internal
import renderer.tools as tools
import renderer.utils as utils
import renderer.mathtools as mathtools
init()

def tileMerge(images: Union[str, dict], verbosityLevel=1, saveImages=True, saveDir="tiles/", zoom=[], logPrefix=""):
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

def render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, verbosityLevel=1, saveImages=True, saveDir="", assetsDir="skins/assets/", logPrefix="", tiles=None):
    if maxZoom < minZoom:
        raise ValueError("Max zoom value is greater than min zoom value")
    tileReturn = {}
    
    # integrity checks
    internal.log("Validating skin...", 0, verbosityLevel, logPrefix)
    utils.skinJsonIntegrity(skinJson)
    internal.log("Validating PLAs...", 0, verbosityLevel, logPrefix)
    utils.plaJsonIntegrity(plaList, nodeList)
    internal.log("Validating nodes...", 0, verbosityLevel, logPrefix)
    utils.nodeJsonIntegrity(nodeList)

    #finds which tiles to render
    if tiles != None:
        utils.tileCoordListIntegrity(tiles, minZoom, maxZoom)
    else: #finds box of tiles
        tiles = tools.plaJsonToTiles(plaList, nodeList, minZoom, maxZoom, maxZoomRange)
    internal.log("Tiles to be generated found", 2, verbosityLevel, logPrefix)

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
    internal.log("Sorted PLA by tiles", 2, verbosityLevel, logPrefix)
    
    #print(tileList)
    
    processStart = time.time() * 1000
    processed = 0
    internal.log("Starting processing...", 0, verbosityLevel, logPrefix)
    for tilePlas in tileList.keys():
        #sort PLAs in tiles by layer
        newTilePlas = {}
        for pla in tileList[tilePlas].keys():
            if not str(float(tileList[tilePlas][pla]['layer'])) in newTilePlas.keys():
                newTilePlas[str(float(tileList[tilePlas][pla]['layer']))] = {}
            newTilePlas[str(float(tileList[tilePlas][pla]['layer']))][pla] = tileList[tilePlas][pla]
        internal.log(f"{tilePlas}: Sorted PLA by layer", 2, verbosityLevel, logPrefix)

        #sort PLAs in layers in files by type
        for layer in newTilePlas.keys():
            #print(newTilePlas[layer].items())
            newTilePlas[layer] = {k: v for k, v in sorted(newTilePlas[layer].items(), key=lambda x: skinJson['order'].index(x[1]['type'].split(' ')[0]))}
        internal.log(f"{tilePlas}: Sorted PLA by type", 2, verbosityLevel, logPrefix)
        
        #merge layers
        tileList[tilePlas] = {}
        layers = sorted(newTilePlas.keys(), key=lambda x: float(x))
        for layer in layers:
            for key, pla in newTilePlas[layer].items():
                tileList[tilePlas][key] = pla
        internal.log(f"{tilePlas}: Merged layers", 2, verbosityLevel, logPrefix)
        
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
        internal.log("PLAs grouped", 2, verbosityLevel, logPrefix)

        processed += 1
        timeLeft = round(((int(round(time.time() * 1000)) - processStart) / processed * (len(tileList) - processed)), 2)
        #logging.info('tile %d/%d [%d, %d] (%s left)', processed, len(tileList), x, y, msToTime(timeLeft))
        internal.log(f"Processed {tilePlas} ({round(processed/len(tileList)*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)
    
    #count # of rendering operations
    internal.log("Counting no. of operations...", 0, verbosityLevel, logPrefix)
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
        internal.log(f"{tilePlas} counted", 2, verbosityLevel, logPrefix)
    
    #render
    operated = 0
    renderStart = time.time() * 1000
    internal.log("Starting render...", 0, verbosityLevel, logPrefix)
    for tilePlas in tileList.keys():
        if tileList[tilePlas] == [{}]:
            if operated != 0:
                timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
                internal.log(f"Rendered {tilePlas} ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 0, verbosityLevel, logPrefix)
            else:
                internal.log(f"Rendered {tilePlas}", 0, verbosityLevel, logPrefix)
            continue
        
        size = maxZoomRange*2**(maxZoom-internal.strToTuple(tilePlas)[0])
        im = Image.new(mode = "RGBA", size = (skinJson['info']['size'], skinJson['info']['size']), color = tuple(skinJson['info']['background']))
        img = ImageDraw.Draw(im)
        textList = []
        pointsTextList = []
        internal.log(f"{tilePlas}: Initialised canvas", 2, verbosityLevel, logPrefix)

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
                        internal.log(f"{tilePlas}: {plaId}: Text length calculated", 2, verbosityLevel, logPrefix)
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
                                internal.log(f"{tilePlas}: {plaId}: Name text generated", 2, verbosityLevel, logPrefix)
                            if "oneWay" in pla['type'].split(" ")[1:] and textLength <= math.dist(coords[c], coords[c+1]):
                                getFont("b", step['size'])
                                counter = 0
                                t = math.floor(math.dist(coords[c], coords[c+1])/(4*textLength))
                                for tx, ty, _ in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=2*t+1):
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
                                internal.log(f"{tilePlas}: {plaId}: Oneway arrows generated", 2, verbosityLevel, logPrefix)
                                
                    def line_backfore():
                        if not "dash" in step.keys():
                            img.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                            if not "unroundedEnds" in info['tags']:
                                img.ellipse([coords[0][0]-step['width']/2+1, coords[0][1]-step['width']/2+1, coords[0][0]+step['width']/2, coords[0][1]+step['width']/2], fill=step['colour'])
                                img.ellipse([coords[-1][0]-step['width']/2+1, coords[-1][1]-step['width']/2+1, coords[-1][0]+step['width']/2, coords[-1][1]+step['width']/2], fill=step['colour'])
                            internal.log(f"{tilePlas}: {plaId}: Line drawn", 2, verbosityLevel, logPrefix)
                        else:
                            offsetInfo = mathtools.dashOffset(coords, step['dash'][0], step['dash'][1])
                            #print(offsetInfo)
                            for c in range(len(coords)-1):
                                o, emptyStart = offsetInfo[c]
                                for dashCoords in mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['dash'][0], step['dash'][1], o, emptyStart):
                                    #print(dashCoords)
                                    img.line(dashCoords, fill=step['colour'], width=step['width'])                
                                internal.log(f"{tilePlas}: {plaId}: Dashes drawn for section {c+1} of {len(coords)}", 2, verbosityLevel, logPrefix)
                            internal.log(f"{tilePlas}: {plaId}: Dashes drawn", 2, verbosityLevel, logPrefix)

                    def area_bordertext():
                        font = getFont("", step['size'])
                        textLength = int(img.textlength(pla['displayname'], font))
                        internal.log(f"{tilePlas}: {plaId}: Text length calculated", 2, verbosityLevel, logPrefix)
                        for c1 in range(len(coords)):
                            c2 = c1+1 if c1 != len(coords)-1 else 0
                            if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= math.dist(coords[c1], coords[c2]):
                                #coords[c]
                                t = math.floor(math.dist(coords[c1], coords[c2])/(4*textLength))
                                t = 1 if t == 0 else t
                                allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1], step['offset'], n=t, returnBoth=True)
                                internal.log(f"{tilePlas}: {plaId}: Midpoints calculated", 2, verbosityLevel, logPrefix)
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
                                    internal.log(f"{tilePlas}: {plaId}: Text {n+1} of {len(allPoints)} generated in section {c1} of {len(coords)+1}", 2, verbosityLevel, logPrefix)

                    def area_centertext():
                        cx, cy = mathtools.polyCenter(coords)
                        internal.log(f"{tilePlas}: {plaId}: Center calculated", 2, verbosityLevel, logPrefix)
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
                            internal.log(f"{tilePlas}: {plaId}: Stripes generated", 2, verbosityLevel, logPrefix)
                            i = i.rotate(step['stripe'][2], center=mathtools.polyCenter(coords))
                            mi = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                            md = ImageDraw.Draw(mi)
                            md.polygon(coords, fill=step['colour'])
                            pi = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                            pi.paste(i, (0, 0), mi)
                            im.paste(pi, (0, 0), pi)
                        else:
                            img.polygon(coords, fill=step['colour'], outline=step['outline'])
                        internal.log(f"{tilePlas}: {plaId}: Area filled", 2, verbosityLevel, logPrefix)
                        outlineCoords = coords[:]
                        outlineCoords.append(outlineCoords[0])
                        img.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                        if not "unroundedEnds" in info['tags']:
                            img.ellipse([coords[0][0]-step['width']/2+1, coords[0][1]-step['width']/2+1, coords[0][0]+step['width']/2, coords[0][1]+step['width']/2], fill=step['colour'])
                        internal.log(f"{tilePlas}: {plaId}: Outline drawn", 2, verbosityLevel, logPrefix)

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
                    internal.log(f"Rendered step {style.index(step)+1} of {len(style)} of {plaId} ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)

                if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                    nodes = []
                    for pla in group.values():
                        nodes += pla['nodes']
                    connectedPre = [tools.findPlasAttachedToNode(x, plaList) for x in nodes]
                    connected = []
                    for i in connectedPre:
                       connected += i
                    internal.log(f"{tilePlas}: Connected lines found", 2, verbosityLevel, logPrefix)
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
                            internal.log(f"{tilePlas}: Coords extracted", 2, verbosityLevel, logPrefix)

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
                            internal.log(f"{tilePlas}: Coords processed", 2, verbosityLevel, logPrefix)
                            if not "dash" in conStep.keys():
                                img.line(conCoords, fill=conStep['colour'], width=conStep['width'], joint="curve")
                                img.ellipse([conCoords[0][0]-conStep['width']/2+1, conCoords[0][1]-conStep['width']/2+1, conCoords[0][0]+conStep['width']/2, conCoords[0][1]+conStep['width']/2], fill=step['colour'])
                                img.ellipse([conCoords[-1][0]-conStep['width']/2+1, conCoords[-1][1]-conStep['width']/2+1, conCoords[-1][0]+conStep['width']/2, conCoords[-1][1]+conStep['width']/2], fill=step['colour'])

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
                            internal.log(f"{tilePlas}: Segment drawn", 2, verbosityLevel, logPrefix)
                    operated += 1
                    timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
                    internal.log(f"Rendered road studs ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)

        textList += pointsTextList 
        textList.reverse()
        dontCross = []
        #print(textList)
        for i, x, y, w, h, rot in textList:
            r = lambda a,b : mathtools.rotateAroundPivot(a, b, x, y, rot)
            currentBoxCoords = [r(x-w/2, y-h/2), r(x-w/2, y+h/2), r(x+w/2, y+h/2), r(x+w/2, y-h/2), r(x-w/2, y-h/2)]
            canPrint = True
            for box in dontCross:
                _1, ox, oy, ow, oh, _2 = textList[dontCross.index(box)]
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
                internal.log(f"{tilePlas}: Text pasted", 2, verbosityLevel, logPrefix)
            else:
                internal.log(f"{tilePlas}: Text skipped", 2, verbosityLevel, logPrefix)
            dontCross.append(currentBoxCoords)
        operated += 1
        timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
        internal.log(f"Rendered text ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)
        
        tileReturn[tilePlas] = im
        if saveImages:
            im.save(f'{saveDir}{tilePlas}.png', 'PNG')

        if operated != 0:
            timeLeft = round(((int(round(time.time() * 1000)) - renderStart) / operated * (operations - operated)), 2)
            internal.log(f"Rendered {tilePlas} ({round(operated/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 0, verbosityLevel, logPrefix)
        else:
            internal.log(f"Rendered {tilePlas}", 0, verbosityLevel, logPrefix)

    internal.log("Render complete", 0, verbosityLevel, logPrefix)

    return tileReturn

def _prerender(tiles, plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, **kwargs):
    return render(plaList, nodeList, minZoom, maxZoom, maxZoomRange, **kwargs, tiles=tiles)

def render_multiprocess(processes: int, plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int, **kwargs):
    #print(__name__)
    if __name__ == 'renderer':
        if not 'tiles' in kwargs.keys() or kwargs['tiles'] == None:
            tiles = tools.plaJsonToTiles(plaList, nodeList, minZoom, maxZoom, maxZoomRange)
        else:
            tiles = kwargs['tiles']
        for i in range(len(tiles)):
            tiles[i] = (tiles[i], plaList, nodeList, minZoom, maxZoom, maxZoomRange, kwargs)
        p = multiprocessing.Pool(processes)
        try:
            print(tiles)
            preresult = list(tqdm.tqdm(p.imap(_prerender, tiles), total=len(tiles)))
        except KeyboardInterrupt:
            p.terminate()
            sys.exit()
        result = {}
        for i in preresult:
            if i == {}:
                continue
            k, v = list(i.items())[0]
            result[k] = v
        return result