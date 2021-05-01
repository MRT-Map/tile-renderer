import math
from PIL import Image, ImageDraw, ImageFont
from typing import Union
import time
import blessed
import multiprocessing
term = blessed.Terminal()

import renderer.internal as internal
import renderer.tools as tools
import renderer.validate as validate
import renderer.mathtools as mathtools

def tiles(args):
    operated, tileCoords, tilePlas, operations, plaList, nodeList, skinJson, _, maxZoom, maxZoomRange, verbosityLevel, saveImages, saveDir, assetsDir, logPrefix, processes = args # _ is minZoom
    #print(operations)
    pid = multiprocessing.current_process()._identity[0] - 1
    start = time.time() * 1000
    
    def pLog(msg):
        #lock.acquire()
        #print(term.move_up(processes - pid + 1), end="")
        if operated.value != 0 and operations != 0:
            print(term.bright_green(f"{pid} | ")+term.green(f"{internal.percentage(operated.value, operations)}% | {internal.msToTime(internal.timeRemaining(start, operated.value, operations))} left | ") + f"{tileCoords}: " + term.bright_black(msg), end=term.clear_eol+"\r")
        else:
            print(term.bright_green(f"{pid} | ")+term.green(f"00.0% | 0.0s left | ") + f"{tileCoords}: " + term.bright_black(msg), end=term.clear_eol+"\r")
        #print(term.move_down(processes - pid + 1), end="")
        #print("asdfasdfasdfsd")
        #lock.release()

    if tilePlas == [{}]:
        if operated.value != 0:
            #timeLeft = round(((int(round(time.time() * 1000)) - start) / operated.value * (operations - operated.value)), 2)
            #internal.log(f"Rendered {tileCoords} ({round(operated.value/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 0, verbosityLevel, logPrefix)
            pLog("Rendered")
        else:
            #internal.log(f"Rendered {tileCoords}", 0, verbosityLevel, logPrefix)
            pLog("Rendered")
        #continue
        return None
    
    pLog("Initialising canvas")
    size = maxZoomRange*2**(maxZoom-internal.strToTuple(tileCoords)[0])
    im = Image.new(mode = "RGBA", size = (skinJson['info']['size'], skinJson['info']['size']), color = tuple(skinJson['info']['background']))
    img = ImageDraw.Draw(im)
    textList = []
    pointsTextList = []
    #internal.log(f"{tileCoords}: Initialised canvas", 2, verbosityLevel, logPrefix)

    def getFont(f: str, s: int):
        if f in skinJson['info']['font'].keys():
            #print(assetsDir+skinJson['info']['font'][f])
            return ImageFont.truetype(assetsDir+skinJson['info']['font'][f], s)
        raise ValueError

    #im.save(f'tiles/{tileCoords}.png', 'PNG')
    for group in tilePlas:
        #print(group)
        info = skinJson['types'][list(group.values())[0]['type'].split(" ")[0]]
        style = []
        for zoom in info['style'].keys():
            if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tileCoords)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                style = info['style'][zoom]
                break
        for step in style:
            for plaId, pla in group.items():
                coords = [(x - internal.strToTuple(tileCoords)[1] * size, y - internal.strToTuple(tileCoords)[2] * size) for x, y in tools.nodes.toCoords(pla['nodes'], nodeList)]
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
                    pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Calculating text length")
                    font = getFont("", step['size'])
                    textLength = int(img.textlength(pla['displayname'], font))
                    if textLength == 0:
                        textLength = int(img.textlength("----------", font))
                    #internal.log(f"{tileCoords}: {plaId}: Text length calculated", 2, verbosityLevel, logPrefix)
                    for c in range(len(coords)-1):
                        #print(coords)
                        #print(mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']))
                        t = math.floor(math.dist(coords[c], coords[c+1])/(4*textLength))
                        t = 1 if t == 0 else t
                        if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= math.dist(coords[c], coords[c+1]):
                            #print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset']))     
                            pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Generating name text")
                            for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=t):
                                i = Image.new('RGBA', (2*textLength,2*(step['size']+4)), (0, 0, 0, 0))
                                d = ImageDraw.Draw(i)
                                d.text((textLength, step['size']+4), pla["displayname"], fill=step['colour'], font=font, anchor="mm")
                                tw, th = i.size[:]
                                i = i.rotate(trot, expand=True)
                                textList.append((i, tx, ty, tw, th, trot))
                            #internal.log(f"{tileCoords}: {plaId}: Name text generated", 2, verbosityLevel, logPrefix)
                        if "oneWay" in pla['type'].split(" ")[1:] and textLength <= math.dist(coords[c], coords[c+1]):
                            pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Generating oneway arrows")
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
                            #internal.log(f"{tileCoords}: {plaId}: Oneway arrows generated", 2, verbosityLevel, logPrefix)
                            
                def line_backfore():
                    if not "dash" in step.keys():
                        pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Drawing line")
                        img.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                        if not "unroundedEnds" in info['tags']:
                            img.ellipse([coords[0][0]-step['width']/2+1, coords[0][1]-step['width']/2+1, coords[0][0]+step['width']/2, coords[0][1]+step['width']/2], fill=step['colour'])
                            img.ellipse([coords[-1][0]-step['width']/2+1, coords[-1][1]-step['width']/2+1, coords[-1][0]+step['width']/2, coords[-1][1]+step['width']/2], fill=step['colour'])
                        #internal.log(f"{tileCoords}: {plaId}: Line drawn", 2, verbosityLevel, logPrefix)
                    else:
                        offsetInfo = mathtools.dashOffset(coords, step['dash'][0], step['dash'][1])
                        #print(offsetInfo)
                        for c in range(len(coords)-1):
                            pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Drawing dashes for section {c+1} of {len(coords)}")
                            o, emptyStart = offsetInfo[c]
                            for dashCoords in mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['dash'][0], step['dash'][1], o, emptyStart):
                                #print(dashCoords)
                                img.line(dashCoords, fill=step['colour'], width=step['width'])                
                            #internal.log(f"{tileCoords}: {plaId}: Dashes drawn for section {c+1} of {len(coords)}", 2, verbosityLevel, logPrefix)
                        #internal.log(f"{tileCoords}: {plaId}: Dashes drawn", 2, verbosityLevel, logPrefix)

                def area_bordertext():
                    pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Calculating text length")
                    font = getFont("", step['size'])
                    textLength = int(img.textlength(pla['displayname'], font))
                    #internal.log(f"{tileCoords}: {plaId}: Text length calculated", 2, verbosityLevel, logPrefix)
                    for c1 in range(len(coords)):
                        c2 = c1+1 if c1 != len(coords)-1 else 0
                        if mathtools.lineInBox(coords, 0, skinJson['info']['size'], 0, skinJson['info']['size']) and 2*textLength <= math.dist(coords[c1], coords[c2]):
                            #coords[c]
                            pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Midpoints calcuated")
                            t = math.floor(math.dist(coords[c1], coords[c2])/(4*textLength))
                            t = 1 if t == 0 else t
                            allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1], step['offset'], n=t, returnBoth=True)
                            #internal.log(f"{tileCoords}: {plaId}: Midpoints calculated", 2, verbosityLevel, logPrefix)
                            for n in range(0, len(allPoints), 2):
                                pLog(f"{style.index(step)+1}/{len(style)} {plaId}: {plaId}: Generating text {n+1} of {len(allPoints)} in section {c1} of {len(coords)+1}")
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
                                #internal.log(f"{tileCoords}: {plaId}: Text {n+1} of {len(allPoints)} generated in section {c1} of {len(coords)+1}", 2, verbosityLevel, logPrefix)

                def area_centertext():
                    pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Calculating center")
                    cx, cy = mathtools.polyCenter(coords)
                    #internal.log(f"{tileCoords}: {plaId}: Center calculated", 2, verbosityLevel, logPrefix)
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
                        pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Generating stripes")
                        xMax, xMin, yMax, yMin = tools.line.findEnds(coords)
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
                        #internal.log(f"{tileCoords}: {plaId}: Stripes generated", 2, verbosityLevel, logPrefix)
                        i = i.rotate(step['stripe'][2], center=mathtools.polyCenter(coords))
                        mi = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                        md = ImageDraw.Draw(mi)
                        md.polygon(coords, fill=step['colour'])
                        pi = Image.new("RGBA", (skinJson['info']['size'], skinJson['info']['size']), (0, 0, 0, 0))
                        pi.paste(i, (0, 0), mi)
                        im.paste(pi, (0, 0), pi)
                    else:
                        pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Filling area")
                        img.polygon(coords, fill=step['colour'], outline=step['outline'])
                    #internal.log(f"{tileCoords}: {plaId}: Area filled", 2, verbosityLevel, logPrefix)
                    pLog(f"{style.index(step)+1}/{len(style)} {plaId}: Drawing outline")
                    outlineCoords = coords[:]
                    outlineCoords.append(outlineCoords[0])
                    img.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                    if not "unroundedEnds" in info['tags']:
                        img.ellipse([coords[0][0]-step['width']/2+1, coords[0][1]-step['width']/2+1, coords[0][0]+step['width']/2, coords[0][1]+step['width']/2], fill=step['colour'])
                    #internal.log(f"{tileCoords}: {plaId}: Outline drawn", 2, verbosityLevel, logPrefix)

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
                pLog(f"{style.index(step)+1}/{len(style)} {plaId}: ")
                funcs[info['type']][step['layer']]()

                operated.value += 1
                timeLeft = round(((int(round(time.time() * 1000)) - start) / operated.value * (operations - operated.value)), 2)
                #internal.log(f"Rendered step {style.index(step)+1} of {len(style)} of {plaId} ({round(operated.value/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)

            if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                pLog("Studs: Finding connected lines")
                nodes = []
                for pla in group.values():
                    nodes += pla['nodes']
                connectedPre = [tools.nodes.findPlasAttached(x, plaList) for x in nodes]
                connected = []
                for i in connectedPre:
                    connected += i
                #internal.log(f"{tileCoords}: Connected lines found", 2, verbosityLevel, logPrefix)
                for conPla, index in connected:
                    if not "road" in skinJson['types'][plaList[conPla]['type'].split(" ")[0]]['tags']:
                        continue
                    conInfo = skinJson['types'][plaList[conPla]['type'].split(" ")[0]]
                    conStyle = []
                    for zoom in conInfo['style'].keys():
                        if maxZoom-internal.strToTuple(zoom)[1] <= internal.strToTuple(tileCoords)[0] <= maxZoom-internal.strToTuple(zoom)[0]:
                            conStyle = conInfo['style'][zoom]
                            break
                    for conStep in conStyle:
                        if conStep['layer'] in ["back", "text"]:
                            continue
                        
                        pLog("Studs: Extracting coords")
                        conCoords = [(x-internal.strToTuple(tileCoords)[1]*size, y-internal.strToTuple(tileCoords)[2]*size) for x,y in tools.nodes.toCoords(plaList[conPla]['nodes'], nodeList)]
                        conCoords = [(int(skinJson['info']['size']/size*x), int(skinJson['info']['size']/size*y)) for x,y in conCoords]
                        preConCoords = conCoords[:]
                        #internal.log(f"{tileCoords}: Coords extracted", 2, verbosityLevel, logPrefix)
                        
                        pLog("Studs: Coords processed")
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
                        #internal.log(f"{tileCoords}: Coords processed", 2, verbosityLevel, logPrefix)
                        pLog("Studs: Segment drawn")
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
                        #internal.log(f"{tileCoords}: Segment drawn", 2, verbosityLevel, logPrefix)
                operated.value += 1
                timeLeft = round(((int(round(time.time() * 1000)) - start) / operated.value * (operations - operated.value)), 2)
                #internal.log(f"Rendered road studs ({round(operated.value/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)

    textList += pointsTextList 
    textList.reverse()
    dontCross = []
    processed = 0
    #print(textList)
    for i, x, y, w, h, rot in textList:
        r = lambda a,b : mathtools.rotateAroundPivot(a, b, x, y, rot)
        currentBoxCoords = [r(x-w/2, y-h/2), r(x-w/2, y+h/2), r(x+w/2, y+h/2), r(x+w/2, y-h/2), r(x-w/2, y-h/2)]
        canPrint = True
        for box in dontCross:
            _, ox, oy, ow, oh, _ = textList[dontCross.index(box)]
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
        processed += 1
        if canPrint:
            pLog(f"Text {processed}/{len(textList)} pasted")
            im.paste(i, (int(x-i.width/2), int(y-i.height/2)), i)
            #internal.log(f"{tileCoords}: Text pasted", 2, verbosityLevel, logPrefix)
        else:
            pLog(f"Text {processed}/{len(textList)} skipped")
            #internal.log(f"{tileCoords}: Text skipped", 2, verbosityLevel, logPrefix)
        dontCross.append(currentBoxCoords)
    operated.value += 1
    timeLeft = round(((int(round(time.time() * 1000)) - start) / operated.value * (operations - operated.value)), 2)
    #internal.log(f"Rendered text ({round(operated.value/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 1, verbosityLevel, logPrefix)
    
    #tileReturn[tileCoords] = im
    if saveImages:
        im.save(f'{saveDir}{tileCoords}.png', 'PNG')

    if operated.value != 0:
        timeLeft = round(((int(round(time.time() * 1000)) - start) / operated.value * (operations - operated.value)), 2)
        pLog("Rendered")
        #internal.log(f"Rendered {tileCoords} ({round(operated.value/operations*100, 2)}%, {internal.msToTime(timeLeft)} remaining)", 0, verbosityLevel, logPrefix)
    else:
        pLog("Rendered")
        #internal.log(f"Rendered {tileCoords}", 0, verbosityLevel, logPrefix)

    return {tileCoords: im}