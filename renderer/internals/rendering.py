import math
from PIL import Image, ImageDraw, ImageFont
import time
import blessed
import multiprocessing
import re
import itertools

import renderer.internals.internal as internal #pylint: disable=import-error
import renderer.tools as tools #pylint: disable=import-error
import renderer.validate as validate #pylint: disable=import-error
import renderer.mathtools as mathtools #pylint: disable=import-error
import renderer.misc as misc #pylint: disable=import-error
term = blessed.Terminal()

def tiles(args):
    lock, operated, start, tile_coords, tile_components, operations, component_json, node_json, skin_json, _, max_zoom, max_zoom_range, save_images, save_dir, assets_dir = args # _ is min_zoom
    #print(operations)
    pid = multiprocessing.current_process()._identity[0] - 1
    
    def p_log(msg):
        #print(term.move_up(processes - pid + 1), end="")
        lock.acquire()
        with term.location():
            if operated.value != 0 and operations != 0:
                print(term.green(f"{internal._percentage(operated.value, operations)}% | {internal.ms_to_time(internal._time_remaining(start, operated.value, operations))} left | ") + f"{pid} | {tile_coords}: " + term.bright_black(msg), end=term.clear_eos + "\r")
            else:
                print(term.green(f"00.0% | 0.0s left | ") + f"{pid} | {tile_coords}: " + term.bright_black(msg), end=term.clear_eos+"\r")
        lock.release()
        #print(term.move_down(processes - pid + 1), end="")

    if tile_components == [{}]:
        p_log("rendered")
        return None
    
    p_log("Initialising canvas")
    size = max_zoom_range*2**(max_zoom - internal._str_to_tuple(tile_coords)[0])
    im = Image.new(mode="RGBA", size=(skin_json['info']['size'], skin_json['info']['size']), color=tuple(skin_json['info']['background']))
    img = ImageDraw.Draw(im)
    text_list = []
    points_text_list = []

    def getFont(f: str, s: int):
        if f in skin_json['info']['font'].keys():
            return ImageFont.truetype(assets_dir+skin_json['info']['font'][f], s)
        raise ValueError

    for group in tile_components:
        info = skin_json['types'][list(group.values())[0]['type'].split(" ")[0]]
        style = []
        for zoom in info['style'].keys():
            if max_zoom-internal._str_to_tuple(zoom)[1] <= internal._str_to_tuple(tile_coords)[0] <= max_zoom-internal._str_to_tuple(zoom)[0]:
                style = info['style'][zoom]
                break
        for step in style:
            for component_id, component in group.items():
                coords = [(x - internal._str_to_tuple(tile_coords)[1] * size, y - internal._str_to_tuple(tile_coords)[2] * size) for x, y in tools.nodes.to_coords(component['nodes'], node_json)]
                coords = [(int(skin_json['info']['size'] / size * x), int(skin_json['info']['size'] / size * y)) for x, y in coords]
                
                def point_circle():
                    img.ellipse([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2], fill=step['colour'], outline=step['outline'], width=step['width'])

                def point_text():
                    font = getFont("", step['size'])
                    textLength = int(img.textlength(component['displayname'], font))
                    i = Image.new('RGBA', (2*textLength, 2*(step['size']+4)), (0, 0, 0, 0))
                    d = ImageDraw.Draw(i)
                    d.text((textLength, step['size']+4), component["displayname"], fill=step['colour'], font=font, anchor="mm")
                    tw, th = i.size
                    points_text_list.append((i, coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1], tw, th, 0))
                    # font = getFont("", step['size'])
                    # img.text((coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1]), component['displayname'], fill=step['colour'], font=font, anchor=step['anchor'])

                def point_square():
                    img.rectangle([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2], fill=step['colour'], outline=step['outline'], width=step['width'])

                def point_image():
                    icon = Image.open(assets_dir+step['file'])
                    im.paste(icon, (int(coords[0][0]-icon.width/2+step['offset'][0]), int(coords[0][1]-icon.height/2+step['offset'][1])), icon)

                def line_text():
                    p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Calculating text length")
                    font = getFont("", step['size'])
                    text_length = int(img.textlength(component['displayname'], font))
                    if text_length == 0:
                        text_length = int(img.textlength("----------", font))
                    for c in range(len(coords)-1):
                        #print(coords)
                        #print(mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']))
                        t = math.floor(math.dist(coords[c], coords[c+1])/(4*text_length))
                        t = 1 if t == 0 else t
                        if mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']) and 2*text_length <= math.dist(coords[c], coords[c + 1]):
                            #print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset']))     
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Generating name text")
                            for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=t):
                                i = Image.new('RGBA', (2*text_length, 2*(step['size']+4)), (0, 0, 0, 0))
                                d = ImageDraw.Draw(i)
                                d.text((text_length, step['size']+4), component["displayname"], fill=step['colour'], font=font, anchor="mm")
                                tw, th = i.size[:]
                                i = i.rotate(trot, expand=True)
                                text_list.append((i, tx, ty, tw, th, trot))
                        if "oneWay" in component['type'].split(" ")[1:] and text_length <= math.dist(coords[c], coords[c + 1]):
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Generating oneway arrows")
                            getFont("b", step['size'])
                            counter = 0
                            t = math.floor(math.dist(coords[c], coords[c+1])/(4*text_length))
                            for tx, ty, _ in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=2*t+1):
                                if counter % 2 == 1:
                                    counter += 1
                                    continue
                                trot = math.degrees(math.atan2(coords[c+1][0]-coords[c][0], coords[c+1][1]-coords[c][1]))
                                i = Image.new('RGBA', (2*text_length, 2*(step['size']+4)), (0, 0, 0, 0))
                                d = ImageDraw.Draw(i)
                                d.text((text_length, step['size']+4), "↓", fill=step['colour'], font=font, anchor="mm")
                                tw, th = i.size[:]
                                i = i.rotate(trot, expand=True)
                                text_list.append((i, tx, ty, tw, th, trot))
                                counter += 1
                            
                def line_backfore():
                    if "dash" not in step.keys():
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Drawing line")
                        img.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                        if "unroundedEnds" not in info['tags']:
                            img.ellipse([coords[0][0]-step['width']/2+1, coords[0][1]-step['width']/2+1, coords[0][0]+step['width']/2, coords[0][1]+step['width']/2], fill=step['colour'])
                            img.ellipse([coords[-1][0]-step['width']/2+1, coords[-1][1]-step['width']/2+1, coords[-1][0]+step['width']/2, coords[-1][1]+step['width']/2], fill=step['colour'])
                    else:
                        offset_info = mathtools.dash_offset(coords, step['dash'][0], step['dash'][1])
                        #print(offset_info)
                        for c in range(len(coords)-1):
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Drawing dashes for section {c + 1} of {len(coords)}")
                            o, empty_start = offset_info[c]
                            for dash_coords in mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['dash'][0], step['dash'][1], o, empty_start):
                                #print(dash_coords)
                                img.line(dash_coords, fill=step['colour'], width=step['width'])

                def area_bordertext():
                    p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Calculating text length")
                    font = getFont("", step['size'])
                    textLength = int(img.textlength(component['displayname'].replace('\n', ''), font))
                    for c1 in range(len(coords)):
                        c2 = c1+1 if c1 != len(coords)-1 else 0
                        if mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']) and 2*textLength <= math.dist(coords[c1], coords[c2]):
                            #coords[c]
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Midpoints calculated")
                            t = math.floor(math.dist(coords[c1], coords[c2])/(4*textLength))
                            t = 1 if t == 0 else t
                            allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1], step['offset'], n=t, return_both=True)
                            for n in range(0, len(allPoints), 2):
                                p_log(f"{style.index(step)+1}/{len(style)} {component_id}: {component_id}: Generating text {n + 1} of {len(allPoints)} in section {c1} of {len(coords) + 1}")
                                points = [allPoints[n], allPoints[n+1]]
                                if step['offset'] < 0:
                                    tx, ty, trot = points[0] if not mathtools.point_in_poly(points[0][0], points[0][1], coords) else points[1]
                                else:
                                    #print(points[0][0], points[0][1], coords)
                                    #print(mathtools.point_in_poly(points[0][0], points[0][1], coords))
                                    tx, ty, trot = points[0] if mathtools.point_in_poly(points[0][0], points[0][1], coords) else points[1]
                                i = Image.new('RGBA', (2*textLength, 2*(step['size']+4)), (0, 0, 0, 0))
                                d = ImageDraw.Draw(i)
                                d.text((textLength, step['size']+4), component["displayname"].replace('\n', ''), fill=step['colour'], font=font, anchor="mm")
                                tw, th = i.size[:]
                                i = i.rotate(trot, expand=True)
                                text_list.append((i, tx, ty, tw, th, trot))

                def area_centertext():
                    p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Calculating center")
                    cx, cy = mathtools.poly_center(coords)
                    cx += step['offset'][0]
                    cy += step['offset'][1]
                    font = getFont("", step['size'])
                    text_length = int(min(img.textlength(x, font) for x in component['displayname'].split('\n')))

                    left = min(c[0] for c in coords)
                    right = max(c[0] for c in coords)
                    dist = right - left
                    if text_length > dist:
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Breaking up string")
                        tokens = component['displayname'].split()
                        wss = re.findall(r"\s+", component['displayname'])
                        text = ""
                        for token, ws in list(itertools.zip_longest(tokens, wss, fillvalue='')):
                            temp_text = text[:]
                            temp_text += token
                            if int(img.textlength(temp_text.split('\n')[-1], font)) > dist:
                                text += '\n'+token+ws
                            else:
                                text += token+ws
                        text_length = int(max(img.textlength(x, font) for x in text.split("\n")))
                        size = int(img.textsize(text, font)[1]+4)
                    else:
                        text = component['displayname']
                        size = step['size']+4

                    i = Image.new('RGBA', (2*text_length, 2*size), (0, 0, 0, 0))
                    d = ImageDraw.Draw(i)
                    cw, ch = i.size
                    d.text((text_length, size), component["displayname"], fill=step['colour'], font=font, anchor="mm")
                    text_list.append((i, cx, cy, cw, ch, 0))

                def area_fill():
                    ai = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                    ad = ImageDraw.Draw(ai)

                    if "stripe" in step.keys():
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Generating stripes")
                        x_max, x_min, y_max, y_min = tools.line.find_ends(coords)
                        x_max += x_max-x_min
                        x_min -= y_max-y_min
                        y_max += x_max-x_min
                        y_min -= y_max-y_min
                        i = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        d = ImageDraw.Draw(i)
                        tlx = x_min-1
                        while tlx <= x_max:
                            d.polygon([(tlx, y_min), (tlx+step['stripe'][0], y_min), (tlx+step['stripe'][0], y_max), (tlx, y_max)], fill=step['colour'])
                            tlx += step['stripe'][0]+step['stripe'][1]
                        i = i.rotate(step['stripe'][2], center=mathtools.poly_center(coords))
                        mi = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        md = ImageDraw.Draw(mi)
                        md.polygon(coords, fill=step['colour'])
                        pi = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        pi.paste(i, (0, 0), mi)
                        ai.paste(pi, (0, 0), pi)
                    else:
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Filling area")
                        ad.polygon(coords, fill=step['colour'], outline=step['outline'])

                    if 'hollows' in component.keys():
                        for n in component['hollows']:
                            nCoords = [(x - internal._str_to_tuple(tile_coords)[1] * size, y - internal._str_to_tuple(tile_coords)[2] * size) for x, y in tools.nodes.to_coords(n, node_json)]
                            nCoords = [(int(skin_json['info']['size'] / size * x), int(skin_json['info']['size'] / size * y)) for x, y in nCoords]
                            ad.polygon(nCoords, fill=(0, 0, 0, 0))
                    im.paste(ai, (0, 0), ai)

                    if step['outline'] is not None:
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Drawing outline")
                        exterior_outline = coords[:]
                        exterior_outline.append(exterior_outline[0])
                        outlines = [exterior_outline]
                        if 'hollows' in component.keys():
                            for n in component['hollows']:
                                nCoords = [(x - internal._str_to_tuple(tile_coords)[1] * size, y - internal._str_to_tuple(tile_coords)[2] * size) for x, y in tools.nodes.to_coords(n, node_json)]
                                nCoords = [(int(skin_json['info']['size'] / size * x), int(skin_json['info']['size'] / size * y)) for x, y in nCoords]
                                nCoords.append(nCoords[0])
                                outlines.append(nCoords)
                        for o_coords in outlines:
                            img.line(o_coords, fill=step['outline'], width=2, joint="curve")
                            if "unroundedEnds" not in info['tags']:
                                img.ellipse([o_coords[0][0]-2/2+1, o_coords[0][1]-2/2+1, o_coords[0][0]+2/2, o_coords[0][1]+2/2], fill=step['outline'])

                def area_centerimage():
                    x, y = mathtools.poly_center(coords)
                    icon = Image.open(assets_dir+step['file'])
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
                p_log(f"{style.index(step)+1}/{len(style)} {component_id}: ")
                funcs[info['type']][step['layer']]()

                operated.value += 1

            if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                p_log("Studs: Finding connected lines")
                nodes = []
                for component in group.values():
                    nodes += component['nodes']
                connected_pre = [tools.nodes.find_components_attached(x, component_json) for x in nodes]
                connected = []
                for i in connected_pre:
                    connected += i
                for con_component, index in connected:
                    if "road" not in skin_json['types'][component_json[con_component]['type'].split(" ")[0]]['tags']:
                        continue
                    con_info = skin_json['types'][component_json[con_component]['type'].split(" ")[0]]
                    con_style = []
                    for zoom in con_info['style'].keys():
                        if max_zoom-internal._str_to_tuple(zoom)[1] <= internal._str_to_tuple(tile_coords)[0] <= max_zoom-internal._str_to_tuple(zoom)[0]:
                            con_style = con_info['style'][zoom]
                            break
                    for con_step in con_style:
                        if con_step['layer'] in ["back", "text"]:
                            continue
                        
                        p_log("Studs: Extracting coords")
                        con_coords = [(x - internal._str_to_tuple(tile_coords)[1] * size, y - internal._str_to_tuple(tile_coords)[2] * size) for x, y in tools.nodes.to_coords(component_json[con_component]['nodes'], node_json)]
                        con_coords = [(int(skin_json['info']['size']/size*x), int(skin_json['info']['size']/size*y)) for x, y in con_coords]
                        preConCoords = con_coords[:]
                        
                        p_log("Studs: Coords processed")
                        if index == 0:
                            con_coords = [con_coords[0], con_coords[1]]
                            if "dash" not in con_step.keys():
                                con_coords[1] = ((con_coords[0][0]+con_coords[1][0])/2, (con_coords[0][1]+con_coords[1][1])/2)
                        elif index == len(con_coords)-1:
                            con_coords = [con_coords[index-1], con_coords[index]]
                            if "dash" not in con_step.keys():
                                con_coords[0] = ((con_coords[0][0]+con_coords[1][0])/2, (con_coords[0][1]+con_coords[1][1])/2)
                        else:
                            con_coords = [con_coords[index-1], con_coords[index], con_coords[index+1]]
                            if "dash" not in con_step.keys():
                                con_coords[0] = ((con_coords[0][0]+con_coords[1][0])/2, (con_coords[0][1]+con_coords[1][1])/2)
                                con_coords[2] = ((con_coords[2][0]+con_coords[1][0])/2, (con_coords[2][1]+con_coords[1][1])/2)
                        p_log("Studs: Segment drawn")
                        if "dash" not in con_step.keys():
                            img.line(con_coords, fill=con_step['colour'], width=con_step['width'], joint="curve")
                            img.ellipse([con_coords[0][0]-con_step['width']/2+1, con_coords[0][1]-con_step['width']/2+1, con_coords[0][0]+con_step['width']/2, con_coords[0][1]+con_step['width']/2], fill=con_step['colour'])
                            img.ellipse([con_coords[-1][0]-con_step['width']/2+1, con_coords[-1][1]-con_step['width']/2+1, con_coords[-1][0]+con_step['width']/2, con_coords[-1][1]+con_step['width']/2], fill=con_step['colour'])

                        else:
                            offset_info = mathtools.dash_offset(preConCoords, con_step['dash'][0], con_step['dash'][1])[index:]
                            #print(offset_info)
                            for c in range(len(con_coords)-1):
                                #print(offset_info)
                                #print(c)
                                o, empty_start = offset_info[c]
                                for dashCoords in mathtools.dash(con_coords[c][0], con_coords[c][1], con_coords[c+1][0], con_coords[c+1][1], con_step['dash'][0], con_step['dash'][1], o, empty_start):
                                    #print(dash_coords)
                                    img.line(dashCoords, fill=con_step['colour'], width=con_step['width'])
                operated.value += 1

    text_list += points_text_list
    text_list.reverse()
    dont_cross = []
    processed = 0
    #print(text_list)
    for i, x, y, w, h, rot in text_list:
        r = lambda a, b: mathtools.rotate_around_pivot(a, b, x, y, rot)
        current_box_coords = [r(x-w/2, y-h/2), r(x-w/2, y+h/2), r(x+w/2, y+h/2), r(x+w/2, y-h/2), r(x-w/2, y-h/2)]
        can_print = True
        for box in dont_cross:
            _, ox, oy, ow, oh, _ = text_list[dont_cross.index(box)]
            o_max_dist = ((ow/2)**2+(oh/2)**2)**0.5/2
            this_max_dist = ((w/2)**2+(h/2)**2)**0.5/2
            dist = ((x-ox)**2+(y-oy)**2)**0.5
            if dist > o_max_dist + this_max_dist:
                continue
            for c in range(len(box)-1):
                for d in range(len(current_box_coords)-1):
                    can_print = False if mathtools.lines_intersect(box[c][0], box[c][1], box[c + 1][0], box[c + 1][1], current_box_coords[d][0], current_box_coords[d][1], current_box_coords[d + 1][0], current_box_coords[d + 1][1]) else can_print
                    if not can_print:
                        break
                if not can_print:
                    break
            if can_print and mathtools.point_in_poly(current_box_coords[0][0], current_box_coords[0][1], box) or mathtools.point_in_poly(box[0][0], box[0][1], current_box_coords):
                can_print = False
            if not can_print:
                break
        processed += 1
        if can_print:
            p_log(f"Text {processed}/{len(text_list)} pasted")
            im.paste(i, (int(x-i.width/2), int(y-i.height/2)), i)
        else:
            p_log(f"Text {processed}/{len(text_list)} skipped")
        dont_cross.append(current_box_coords)
    operated.value += 1
    
    #tileReturn[tile_coords] = im
    if save_images:
        im.save(f'{save_dir}{tile_coords}.png', 'PNG')

    p_log("Rendered")

    return {tile_coords: im}