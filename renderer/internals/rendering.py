import math
from PIL import Image, ImageDraw, ImageFont
import blessed
import re
import itertools

import renderer.internals.internal as internal
import renderer.tools as tools
import renderer.mathtools as mathtools
from renderer.old_types import *
term = blessed.Terminal()

try: import ray
except ModuleNotFoundError: pass

class _Logger:
    def __init__(self, using_ray: bool, operated, operations: int, start: RealNum, tile_coords: TileCoord):
        self.using_ray = using_ray
        self.operated = operated
        self.operations = operations
        self.start = start
        self.tile_coords = tile_coords

    def log(self, msg):
        if self.using_ray: ops = ray.get(self.operated.get.remote())
        else: ops = self.operated.get()
        if ops != 0 and self.operations != 0:
            print(term.green(f"{internal._percentage(ops, self.operations)}% | " +
                             f"{internal._ms_to_time(internal._time_remaining(self.start, ops, self.operations))} left | ") +
                  f"{self.tile_coords}: " + term.bright_black(msg), flush=True)
        else:
            print(term.green(f"00.0% | 0.0s left | ") + f"{self.tile_coords}: " + term.bright_black(msg), flush=True)

def _node_list_to_image_coords(node_list: List[str], node_json: NodeJson, skin_json: SkinJson, tile_coords: str, size: RealNum) -> List[Coord]:
    image_coords = []
    for x, y in tools.nodes.to_coords(node_list, node_json):
        xc = x - internal._str_to_tuple(tile_coords)[1] * size
        yc = y - internal._str_to_tuple(tile_coords)[2] * size
        xs = int(skin_json['info']['size'] / size * xc)
        ys = int(skin_json['info']['size'] / size * yc)
        image_coords.append((xs, ys))
    return image_coords

def _draw_components(operated, operations: int, start: RealNum, tile_coords: str, tile_components: List[dict],
                     component_json, node_json, skin_json, max_zoom, max_zoom_range, save_images, save_dir, assets_dir, using_ray: bool=False):
    logger = _Logger(using_ray, operated, operations, start, internal._str_to_tuple(tile_coords))
    if tile_components == [{}]:
        logger.log("render complete")
        return None

    logger.log("Initialising canvas")
    size = max_zoom_range * 2 ** (max_zoom - internal._str_to_tuple(tile_coords)[0])
    img = Image.new(mode="RGBA", size=(skin_json['info']['size'], skin_json['info']['size']),
                    color=tuple(skin_json['info']['background']))
    imd = ImageDraw.Draw(img)
    text_list = []
    points_text_list = []

    def get_font(style_: str, size_: int) -> ImageFont.FreeTypeFont:
        if style_ in skin_json['info']['font'].keys():
            return ImageFont.truetype(assets_dir + skin_json['info']['font'][style_], size_)
        raise ValueError

    for group in tile_components:
        type_info = skin_json['types'][list(group.values())[0]['type'].split(" ")[0]]
        style = []
        for zoom in type_info['style'].keys():
            if max_zoom - internal._str_to_tuple(zoom)[1] <= internal._str_to_tuple(tile_coords)[0] <= max_zoom - \
                    internal._str_to_tuple(zoom)[0]:
                style = type_info['style'][zoom]
                break
        for step in style:
            for component_id, component in group.items():
                coords = _node_list_to_image_coords(component['nodes'], node_json, skin_json, tile_coords, size)

                def point_circle():
                    imd.ellipse([coords[0][0] - step['size'] / 2 + 1, coords[0][1] - step['size'] / 2 + 1,
                                 coords[0][0] + step['size'] / 2, coords[0][1] + step['size'] / 2],
                                fill=step['colour'], outline=step['outline'], width=step['width'])

                def point_text():
                    font = get_font("", step['size'])
                    text_length = int(imd.textlength(component['displayname'], font))
                    pt_i = Image.new('RGBA', (2 * text_length, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                    pt_d = ImageDraw.Draw(pt_i)
                    pt_d.text((text_length, step['size'] + 4), component["displayname"], fill=step['colour'], font=font,
                              anchor="mm")
                    tw, th = pt_i.size
                    points_text_list.append(
                        (pt_i, coords[0][0] + step['offset'][0], coords[0][1] + step['offset'][1], tw, th, 0))
                    # font = get_font("", step['size'])
                    # img.text((coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1]), component['displayname'], fill=step['colour'], font=font, anchor=step['anchor'])

                def point_square():
                    imd.rectangle([coords[0][0] - step['size'] / 2 + 1, coords[0][1] - step['size'] / 2 + 1,
                                   coords[0][0] + step['size'] / 2, coords[0][1] + step['size'] / 2],
                                  fill=step['colour'], outline=step['outline'], width=step['width'])

                def point_image():
                    icon = Image.open(assets_dir + step['file'])
                    img.paste(icon, (int(coords[0][0] - icon.width / 2 + step['offset'][0]),
                                     int(coords[0][1] - icon.height / 2 + step['offset'][1])), icon)

                def line_text():
                    logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Calculating text length")
                    font = get_font("", step['size'])
                    text_length = int(imd.textlength(component['displayname'], font))
                    if text_length == 0:
                        text_length = int(imd.textlength("----------", font))
                    for c in range(len(coords) - 1):
                        # print(coords)
                        # print(mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']))
                        t = math.floor(math.dist(coords[c], coords[c + 1]) / (4 * text_length))
                        t = 1 if t == 0 else t
                        if mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']) \
                                and 2 * text_length <= math.dist(coords[c], coords[c + 1]):
                            # print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset']))
                            logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Generating name text")
                            for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c + 1][0],
                                                                   coords[c + 1][1], step['offset'], n=t):
                                lt_i = Image.new('RGBA', (2 * text_length, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                                lt_d = ImageDraw.Draw(lt_i)
                                lt_d.text((text_length, step['size'] + 4), component["displayname"],
                                          fill=step['colour'], font=font, anchor="mm")
                                tw, th = lt_i.size[:]
                                lt_i = lt_i.rotate(trot, expand=True)
                                text_list.append((lt_i, tx, ty, tw, th, trot))
                        if "oneWay" in component['type'].split(" ")[1:] and text_length <= math.dist(coords[c],
                                                                                                     coords[c + 1]):
                            logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Generating oneway arrows")
                            get_font("b", step['size'])
                            counter = 0
                            t = math.floor(math.dist(coords[c], coords[c + 1]) / (4 * text_length))
                            for tx, ty, _ in mathtools.midpoint(coords[c][0], coords[c][1], coords[c + 1][0],
                                                                coords[c + 1][1], step['offset'], n=2 * t + 1):
                                if counter % 2 == 1:
                                    counter += 1
                                    continue
                                trot = math.degrees(
                                    math.atan2(coords[c + 1][0] - coords[c][0], coords[c + 1][1] - coords[c][1]))
                                lt_i = Image.new('RGBA', (2 * text_length, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                                lt_d = ImageDraw.Draw(lt_i)
                                lt_d.text((text_length, step['size'] + 4), "↓", fill=step['colour'], font=font,
                                          anchor="mm")
                                tw, th = lt_i.size[:]
                                lt_i = lt_i.rotate(trot, expand=True)
                                text_list.append((lt_i, tx, ty, tw, th, trot))
                                counter += 1

                def line_backfore():
                    if "dash" not in step.keys():
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Drawing line")
                        imd.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                        if "unroundedEnds" not in type_info['tags']:
                            imd.ellipse([coords[0][0] - step['width'] / 2 + 1, coords[0][1] - step['width'] / 2 + 1,
                                         coords[0][0] + step['width'] / 2, coords[0][1] + step['width'] / 2],
                                        fill=step['colour'])
                            imd.ellipse([coords[-1][0] - step['width'] / 2 + 1, coords[-1][1] - step['width'] / 2 + 1,
                                         coords[-1][0] + step['width'] / 2, coords[-1][1] + step['width'] / 2],
                                        fill=step['colour'])
                    else:
                        offset_info = mathtools.dash_offset(coords, step['dash'][0], step['dash'][1])
                        # print(offset_info)
                        for c in range(len(coords) - 1):
                            logger.log(
                                f"{style.index(step) + 1}/{len(style)} {component_id}: Drawing dashes for section {c + 1} of {len(coords)}")
                            o, empty_start = offset_info[c]
                            for dash_coords in mathtools.dash(coords[c][0], coords[c][1], coords[c + 1][0],
                                                              coords[c + 1][1], step['dash'][0], step['dash'][1], o,
                                                              empty_start):
                                # print(dash_coords)
                                imd.line(dash_coords, fill=step['colour'], width=step['width'])

                def area_bordertext():
                    logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Calculating text length")
                    font = get_font("", step['size'])
                    textLength = int(imd.textlength(component['displayname'].replace('\n', ''), font))
                    for c1 in range(len(coords)):
                        c2 = c1 + 1 if c1 != len(coords) - 1 else 0
                        if mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0,
                                                 skin_json['info']['size']) and 2 * textLength <= math.dist(coords[c1],
                                                                                                            coords[c2]):
                            # coords[c]
                            logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Midpoints calculated")
                            t = math.floor(math.dist(coords[c1], coords[c2]) / (4 * textLength))
                            t = 1 if t == 0 else t
                            allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1],
                                                           step['offset'], n=t, return_both=True)
                            for n in range(0, len(allPoints), 2):
                                logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: {component_id}: " +
                                           f"Generating text {n + 1} of {len(allPoints)} in section {c1} of {len(coords) + 1}")
                                points = [allPoints[n], allPoints[n + 1]]
                                if step['offset'] < 0:
                                    tx, ty, trot = points[0] if not mathtools.point_in_poly(points[0][0], points[0][1],
                                                                                            coords) else points[1]
                                else:
                                    # print(points[0][0], points[0][1], coords)
                                    # print(mathtools.point_in_poly(points[0][0], points[0][1], coords))
                                    tx, ty, trot = points[0] if mathtools.point_in_poly(points[0][0], points[0][1],
                                                                                        coords) else points[1]
                                abt_i = Image.new('RGBA', (2 * textLength, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                                abt_d = ImageDraw.Draw(abt_i)
                                abt_d.text((textLength, step['size'] + 4), component["displayname"].replace('\n', ''),
                                           fill=step['colour'], font=font, anchor="mm")
                                tw, th = abt_i.size[:]
                                abt_i = abt_i.rotate(trot, expand=True)
                                text_list.append((abt_i, tx, ty, tw, th, trot))

                def area_centertext():
                    logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Calculating center")
                    cx, cy = mathtools.poly_center(coords)
                    cx += step['offset'][0]
                    cy += step['offset'][1]
                    font = get_font("", step['size'])
                    text_length = int(min(imd.textlength(x, font) for x in component['displayname'].split('\n')))

                    left = min(c[0] for c in coords)
                    right = max(c[0] for c in coords)
                    delta = right - left
                    if text_length > delta:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Breaking up string")
                        tokens = component['displayname'].split()
                        wss = re.findall(r"\s+", component['displayname'])
                        text = ""
                        for token, ws in list(itertools.zip_longest(tokens, wss, fillvalue='')):
                            temp_text = text[:]
                            temp_text += token
                            if int(imd.textlength(temp_text.split('\n')[-1], font)) > delta:
                                text += '\n' + token + ws
                            else:
                                text += token + ws
                        text_length = int(max(imd.textlength(x, font) for x in text.split("\n")))
                        text_size = int(imd.textsize(text, font)[1] + 4)
                    else:
                        text = component['displayname']
                        text_size = step['size'] + 4

                    act_i = Image.new('RGBA', (2 * text_length, 2 * text_size), (0, 0, 0, 0))
                    act_d = ImageDraw.Draw(act_i)
                    cw, ch = act_i.size
                    act_d.text((text_length, text_size), text, fill=step['colour'], font=font, anchor="mm")
                    text_list.append((act_i, cx, cy, cw, ch, 0))

                def area_fill():
                    ai = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                    ad = ImageDraw.Draw(ai)

                    if "stripe" in step.keys():
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Generating stripes")
                        x_max, x_min, y_max, y_min = tools.line.find_ends(coords)
                        x_max += x_max - x_min
                        x_min -= y_max - y_min
                        y_max += x_max - x_min
                        y_min -= y_max - y_min
                        af_i = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        af_d = ImageDraw.Draw(af_i)
                        tlx = x_min - 1
                        while tlx <= x_max:
                            af_d.polygon(
                                [(tlx, y_min), (tlx + step['stripe'][0], y_min), (tlx + step['stripe'][0], y_max),
                                 (tlx, y_max)], fill=step['colour'])
                            tlx += step['stripe'][0] + step['stripe'][1]
                        af_i = af_i.rotate(step['stripe'][2], center=mathtools.poly_center(coords))
                        mi = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        md = ImageDraw.Draw(mi)
                        md.polygon(coords, fill=step['colour'])
                        pi = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        pi.paste(af_i, (0, 0), mi)
                        ai.paste(pi, (0, 0), pi)
                    else:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Filling area")
                        ad.polygon(coords, fill=step['colour'], outline=step['outline'])

                    if 'hollows' in component.keys():
                        for n in component['hollows']:
                            n_coords = _node_list_to_image_coords(n, node_json, skin_json, tile_coords, size)
                            ad.polygon(n_coords, fill=(0, 0, 0, 0))
                    img.paste(ai, (0, 0), ai)

                    if step['outline'] is not None:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: Drawing outline")
                        exterior_outline = coords[:]
                        exterior_outline.append(exterior_outline[0])
                        outlines = [exterior_outline]
                        if 'hollows' in component.keys():
                            for n in component['hollows']:
                                n_coords = _node_list_to_image_coords(n, node_json, skin_json, tile_coords, size)
                                n_coords.append(n_coords[0])
                                outlines.append(n_coords)
                        for o_coords in outlines:
                            imd.line(o_coords, fill=step['outline'], width=2, joint="curve")
                            if "unroundedEnds" not in type_info['tags']:
                                imd.ellipse(
                                    [o_coords[0][0] - 2 / 2 + 1, o_coords[0][1] - 2 / 2 + 1, o_coords[0][0] + 2 / 2,
                                     o_coords[0][1] + 2 / 2], fill=step['outline'])

                def area_centerimage():
                    cx, cy = mathtools.poly_center(coords)
                    icon = Image.open(assets_dir + step['file'])
                    img.paste(i, (cx + step['offset'][0], cy + step['offset'][1]), icon)

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

                if step['layer'] not in funcs[type_info['type']].keys():
                    raise KeyError(f"{step['layer']} is not a valid layer")
                logger.log(f"{style.index(step) + 1}/{len(style)} {component_id}: ")
                funcs[type_info['type']][step['layer']]()

                if using_ray:
                    operated.count.remote()
                else:
                    operated.count()

            if type_info['type'] == "line" and "road" in type_info['tags'] and step['layer'] == "back":
                logger.log("Studs: Finding connected lines")
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
                        if max_zoom - internal._str_to_tuple(zoom)[1]\
                                <= internal._str_to_tuple(tile_coords)[0]\
                                <= max_zoom - internal._str_to_tuple(zoom)[0]:
                            con_style = con_info['style'][zoom]
                            break
                    for con_step in con_style:
                        if con_step['layer'] in ["back", "text"]:
                            continue

                        logger.log("Studs: Extracting coords")
                        con_coords = _node_list_to_image_coords(component_json[con_component]['nodes'], node_json,
                                                                skin_json, tile_coords, size)
                        pre_con_coords = con_coords[:]

                        logger.log("Studs: Coords processed")
                        if index == 0:
                            con_coords = [con_coords[0], con_coords[1]]
                            if "dash" not in con_step.keys():
                                con_coords[1] = (
                                (con_coords[0][0] + con_coords[1][0]) / 2, (con_coords[0][1] + con_coords[1][1]) / 2)
                        elif index == len(con_coords) - 1:
                            con_coords = [con_coords[index - 1], con_coords[index]]
                            if "dash" not in con_step.keys():
                                con_coords[0] = (
                                (con_coords[0][0] + con_coords[1][0]) / 2, (con_coords[0][1] + con_coords[1][1]) / 2)
                        else:
                            con_coords = [con_coords[index - 1], con_coords[index], con_coords[index + 1]]
                            if "dash" not in con_step.keys():
                                con_coords[0] = (
                                (con_coords[0][0] + con_coords[1][0]) / 2, (con_coords[0][1] + con_coords[1][1]) / 2)
                                con_coords[2] = (
                                (con_coords[2][0] + con_coords[1][0]) / 2, (con_coords[2][1] + con_coords[1][1]) / 2)
                        logger.log("Studs: Segment drawn")
                        if "dash" not in con_step.keys():
                            imd.line(con_coords, fill=con_step['colour'], width=con_step['width'], joint="curve")
                            imd.ellipse([con_coords[0][0] - con_step['width'] / 2 + 1,
                                         con_coords[0][1] - con_step['width'] / 2 + 1,
                                         con_coords[0][0] + con_step['width'] / 2,
                                         con_coords[0][1] + con_step['width'] / 2], fill=con_step['colour'])
                            imd.ellipse([con_coords[-1][0] - con_step['width'] / 2 + 1,
                                         con_coords[-1][1] - con_step['width'] / 2 + 1,
                                         con_coords[-1][0] + con_step['width'] / 2,
                                         con_coords[-1][1] + con_step['width'] / 2], fill=con_step['colour'])

                        else:
                            con_offset_info = mathtools.dash_offset(pre_con_coords, con_step['dash'][0],
                                                                    con_step['dash'][1])[index:]
                            # print(offset_info)
                            for c in range(len(con_coords) - 1):
                                # print(offset_info)
                                # print(c)
                                con_o, con_empty_start = con_offset_info[c]
                                for con_dash_coords in mathtools.dash(con_coords[c][0], con_coords[c][1],
                                                                      con_coords[c + 1][0], con_coords[c + 1][1],
                                                                      con_step['dash'][0], con_step['dash'][1], con_o,
                                                                      con_empty_start):
                                    # print(dash_coords)
                                    imd.line(con_dash_coords, fill=con_step['colour'], width=con_step['width'])
                if using_ray:
                    operated.count.remote()
                else:
                    operated.count()

    return {tile_coords: img}

def _tile(args, using_ray: bool=False):
    lock, operated, start, tile_coords, tile_components, operations, component_json, node_json, skin_json, _, max_zoom, max_zoom_range, save_images, save_dir, assets_dir = args # _ is min_zoom
    #print(operations)
    
    def p_log(msg):
        #print(term.move_up(processes - pid + 1), end="")
        #lock.acquire()
        with term.location():
            if using_ray: ops = ray.get(operated.get.remote())
            else: ops = operated.get()
            if ops != 0 and operations != 0:
                print(term.green(f"{internal._percentage(ops, operations)}% | " +
                                 f"{internal._ms_to_time(internal._time_remaining(start, ops, operations))} left | ") +
                      f"{tile_coords}: " + term.bright_black(msg), flush=True)
            else:
                print(term.green(f"00.0% | 0.0s left | ") + f"{tile_coords}: " + term.bright_black(msg), flush=True)
        #lock.release()
        #print(term.move_down(processes - pid + 1), end="")

    if tile_components == [{}]:
        p_log("rendered")
        return None
    
    p_log("Initialising canvas")
    size = max_zoom_range*2**(max_zoom - internal._str_to_tuple(tile_coords)[0])
    img = Image.new(mode="RGBA", size=(skin_json['info']['size'], skin_json['info']['size']), color=tuple(skin_json['info']['background']))
    imd = ImageDraw.Draw(img)
    text_list = []
    points_text_list = []

    def get_font(style_: str, size_: int) -> ImageFont.FreeTypeFont:
        if style_ in skin_json['info']['font'].keys():
            return ImageFont.truetype(assets_dir+skin_json['info']['font'][style_], size_)
        raise ValueError

    for group in tile_components:
        type_info = skin_json['types'][list(group.values())[0]['type'].split(" ")[0]]
        style = []
        for zoom in type_info['style'].keys():
            if max_zoom-internal._str_to_tuple(zoom)[1] <= internal._str_to_tuple(tile_coords)[0] <= max_zoom-internal._str_to_tuple(zoom)[0]:
                style = type_info['style'][zoom]
                break
        for step in style:
            for component_id, component in group.items():
                coords = _node_list_to_image_coords(component['nodes'], node_json, skin_json, tile_coords, size)

                def point_circle():
                    imd.ellipse([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2],
                                fill=step['colour'], outline=step['outline'], width=step['width'])

                def point_text():
                    font = get_font("", step['size'])
                    text_length = int(imd.textlength(component['displayname'], font))
                    pt_i = Image.new('RGBA', (2 * text_length, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                    pt_d = ImageDraw.Draw(pt_i)
                    pt_d.text((text_length, step['size'] + 4), component["displayname"], fill=step['colour'], font=font, anchor="mm")
                    tw, th = pt_i.size
                    points_text_list.append((pt_i, coords[0][0] + step['offset'][0], coords[0][1] + step['offset'][1], tw, th, 0))
                    # font = get_font("", step['size'])
                    # img.text((coords[0][0]+step['offset'][0], coords[0][1]+step['offset'][1]), component['displayname'], fill=step['colour'], font=font, anchor=step['anchor'])

                def point_square():
                    imd.rectangle([coords[0][0]-step['size']/2+1, coords[0][1]-step['size']/2+1, coords[0][0]+step['size']/2, coords[0][1]+step['size']/2],
                                  fill=step['colour'], outline=step['outline'], width=step['width'])

                def point_image():
                    icon = Image.open(assets_dir+step['file'])
                    img.paste(icon, (int(coords[0][0]-icon.width/2+step['offset'][0]), int(coords[0][1]-icon.height/2+step['offset'][1])), icon)

                def line_text():
                    p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Calculating text length")
                    font = get_font("", step['size'])
                    text_length = int(imd.textlength(component['displayname'], font))
                    if text_length == 0:
                        text_length = int(imd.textlength("----------", font))
                    for c in range(len(coords)-1):
                        #print(coords)
                        #print(mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']))
                        t = math.floor(math.dist(coords[c], coords[c+1])/(4*text_length))
                        t = 1 if t == 0 else t
                        if mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']) \
                           and 2*text_length <= math.dist(coords[c], coords[c + 1]):
                            #print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset']))     
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Generating name text")
                            for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=t):
                                lt_i = Image.new('RGBA', (2 * text_length, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                                lt_d = ImageDraw.Draw(lt_i)
                                lt_d.text((text_length, step['size'] + 4), component["displayname"], fill=step['colour'], font=font, anchor="mm")
                                tw, th = lt_i.size[:]
                                lt_i = lt_i.rotate(trot, expand=True)
                                text_list.append((lt_i, tx, ty, tw, th, trot))
                        if "oneWay" in component['type'].split(" ")[1:] and text_length <= math.dist(coords[c], coords[c + 1]):
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Generating oneway arrows")
                            get_font("b", step['size'])
                            counter = 0
                            t = math.floor(math.dist(coords[c], coords[c+1])/(4*text_length))
                            for tx, ty, _ in mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['offset'], n=2*t+1):
                                if counter % 2 == 1:
                                    counter += 1
                                    continue
                                trot = math.degrees(math.atan2(coords[c+1][0]-coords[c][0], coords[c+1][1]-coords[c][1]))
                                lt_i = Image.new('RGBA', (2 * text_length, 2 * (step['size'] + 4)), (0, 0, 0, 0))
                                lt_d = ImageDraw.Draw(lt_i)
                                lt_d.text((text_length, step['size'] + 4), "↓", fill=step['colour'], font=font, anchor="mm")
                                tw, th = lt_i.size[:]
                                lt_i = lt_i.rotate(trot, expand=True)
                                text_list.append((lt_i, tx, ty, tw, th, trot))
                                counter += 1
                            
                def line_backfore():
                    if "dash" not in step.keys():
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Drawing line")
                        imd.line(coords, fill=step['colour'], width=step['width'], joint="curve")
                        if "unroundedEnds" not in type_info['tags']:
                            imd.ellipse([coords[0][0]-step['width']/2+1, coords[0][1]-step['width']/2+1, coords[0][0]+step['width']/2, coords[0][1]+step['width']/2],
                                        fill=step['colour'])
                            imd.ellipse([coords[-1][0]-step['width']/2+1, coords[-1][1]-step['width']/2+1, coords[-1][0]+step['width']/2, coords[-1][1]+step['width']/2],
                                        fill=step['colour'])
                    else:
                        offset_info = mathtools.dash_offset(coords, step['dash'][0], step['dash'][1])
                        #print(offset_info)
                        for c in range(len(coords)-1):
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Drawing dashes for section {c + 1} of {len(coords)}")
                            o, empty_start = offset_info[c]
                            for dash_coords in mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step['dash'][0], step['dash'][1], o, empty_start):
                                #print(dash_coords)
                                imd.line(dash_coords, fill=step['colour'], width=step['width'])

                def area_bordertext():
                    p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Calculating text length")
                    font = get_font("", step['size'])
                    textLength = int(imd.textlength(component['displayname'].replace('\n', ''), font))
                    for c1 in range(len(coords)):
                        c2 = c1+1 if c1 != len(coords)-1 else 0
                        if mathtools.line_in_box(coords, 0, skin_json['info']['size'], 0, skin_json['info']['size']) and 2*textLength <= math.dist(coords[c1], coords[c2]):
                            #coords[c]
                            p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Midpoints calculated")
                            t = math.floor(math.dist(coords[c1], coords[c2])/(4*textLength))
                            t = 1 if t == 0 else t
                            allPoints = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1], step['offset'], n=t, return_both=True)
                            for n in range(0, len(allPoints), 2):
                                p_log(f"{style.index(step)+1}/{len(style)} {component_id}: {component_id}: " +
                                      f"Generating text {n + 1} of {len(allPoints)} in section {c1} of {len(coords) + 1}")
                                points = [allPoints[n], allPoints[n+1]]
                                if step['offset'] < 0:
                                    tx, ty, trot = points[0] if not mathtools.point_in_poly(points[0][0], points[0][1], coords) else points[1]
                                else:
                                    #print(points[0][0], points[0][1], coords)
                                    #print(mathtools.point_in_poly(points[0][0], points[0][1], coords))
                                    tx, ty, trot = points[0] if mathtools.point_in_poly(points[0][0], points[0][1], coords) else points[1]
                                abt_i = Image.new('RGBA', (2*textLength, 2*(step['size']+4)), (0, 0, 0, 0))
                                abt_d = ImageDraw.Draw(abt_i)
                                abt_d.text((textLength, step['size']+4), component["displayname"].replace('\n', ''),
                                           fill=step['colour'], font=font, anchor="mm")
                                tw, th = abt_i.size[:]
                                abt_i = abt_i.rotate(trot, expand=True)
                                text_list.append((abt_i, tx, ty, tw, th, trot))

                def area_centertext():
                    p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Calculating center")
                    cx, cy = mathtools.poly_center(coords)
                    cx += step['offset'][0]
                    cy += step['offset'][1]
                    font = get_font("", step['size'])
                    text_length = int(min(imd.textlength(x, font) for x in component['displayname'].split('\n')))

                    left = min(c[0] for c in coords)
                    right = max(c[0] for c in coords)
                    delta = right - left
                    if text_length > delta:
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Breaking up string")
                        tokens = component['displayname'].split()
                        wss = re.findall(r"\s+", component['displayname'])
                        text = ""
                        for token, ws in list(itertools.zip_longest(tokens, wss, fillvalue='')):
                            temp_text = text[:]
                            temp_text += token
                            if int(imd.textlength(temp_text.split('\n')[-1], font)) > delta:
                                text += '\n'+token+ws
                            else:
                                text += token+ws
                        text_length = int(max(imd.textlength(x, font) for x in text.split("\n")))
                        text_size = int(imd.textsize(text, font)[1]+4)
                    else:
                        text = component['displayname']
                        text_size = step['size']+4

                    act_i = Image.new('RGBA', (2*text_length, 2*text_size), (0, 0, 0, 0))
                    act_d = ImageDraw.Draw(act_i)
                    cw, ch = act_i.size
                    act_d.text((text_length, text_size), text, fill=step['colour'], font=font, anchor="mm")
                    text_list.append((act_i, cx, cy, cw, ch, 0))

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
                        af_i = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        af_d = ImageDraw.Draw(af_i)
                        tlx = x_min-1
                        while tlx <= x_max:
                            af_d.polygon([(tlx, y_min), (tlx+step['stripe'][0], y_min), (tlx+step['stripe'][0], y_max), (tlx, y_max)], fill=step['colour'])
                            tlx += step['stripe'][0]+step['stripe'][1]
                        af_i = af_i.rotate(step['stripe'][2], center=mathtools.poly_center(coords))
                        mi = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        md = ImageDraw.Draw(mi)
                        md.polygon(coords, fill=step['colour'])
                        pi = Image.new("RGBA", (skin_json['info']['size'], skin_json['info']['size']), (0, 0, 0, 0))
                        pi.paste(af_i, (0, 0), mi)
                        ai.paste(pi, (0, 0), pi)
                    else:
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Filling area")
                        ad.polygon(coords, fill=step['colour'], outline=step['outline'])

                    if 'hollows' in component.keys():
                        for n in component['hollows']:
                            n_coords = _node_list_to_image_coords(n, node_json, skin_json, tile_coords, size)
                            ad.polygon(n_coords, fill=(0, 0, 0, 0))
                    img.paste(ai, (0, 0), ai)

                    if step['outline'] is not None:
                        p_log(f"{style.index(step)+1}/{len(style)} {component_id}: Drawing outline")
                        exterior_outline = coords[:]
                        exterior_outline.append(exterior_outline[0])
                        outlines = [exterior_outline]
                        if 'hollows' in component.keys():
                            for n in component['hollows']:
                                n_coords = _node_list_to_image_coords(n, node_json, skin_json, tile_coords, size)
                                n_coords.append(n_coords[0])
                                outlines.append(n_coords)
                        for o_coords in outlines:
                            imd.line(o_coords, fill=step['outline'], width=2, joint="curve")
                            if "unroundedEnds" not in type_info['tags']:
                                imd.ellipse([o_coords[0][0]-2/2+1, o_coords[0][1]-2/2+1, o_coords[0][0]+2/2, o_coords[0][1]+2/2], fill=step['outline'])

                def area_centerimage():
                    cx, cy = mathtools.poly_center(coords)
                    icon = Image.open(assets_dir+step['file'])
                    img.paste(i, (cx+step['offset'][0], cy+step['offset'][1]), icon)

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

                if step['layer'] not in funcs[type_info['type']].keys():
                    raise KeyError(f"{step['layer']} is not a valid layer")
                p_log(f"{style.index(step)+1}/{len(style)} {component_id}: ")
                funcs[type_info['type']][step['layer']]()

                if using_ray: operated.count.remote()
                else: operated.count()

            if type_info['type'] == "line" and "road" in type_info['tags'] and step['layer'] == "back":
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
                        con_coords = _node_list_to_image_coords(component_json[con_component]['nodes'], node_json, skin_json, tile_coords, size)
                        pre_con_coords = con_coords[:]
                        
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
                            imd.line(con_coords, fill=con_step['colour'], width=con_step['width'], joint="curve")
                            imd.ellipse([con_coords[0][0]-con_step['width']/2+1, con_coords[0][1]-con_step['width']/2+1, con_coords[0][0]+con_step['width']/2, con_coords[0][1]+con_step['width']/2], fill=con_step['colour'])
                            imd.ellipse([con_coords[-1][0]-con_step['width']/2+1, con_coords[-1][1]-con_step['width']/2+1, con_coords[-1][0]+con_step['width']/2, con_coords[-1][1]+con_step['width']/2], fill=con_step['colour'])

                        else:
                            con_offset_info = mathtools.dash_offset(pre_con_coords, con_step['dash'][0], con_step['dash'][1])[index:]
                            #print(offset_info)
                            for c in range(len(con_coords)-1):
                                #print(offset_info)
                                #print(c)
                                con_o, con_empty_start = con_offset_info[c]
                                for con_dash_coords in mathtools.dash(con_coords[c][0], con_coords[c][1], con_coords[c+1][0], con_coords[c+1][1], con_step['dash'][0], con_step['dash'][1], con_o, con_empty_start):
                                    #print(dash_coords)
                                    imd.line(con_dash_coords, fill=con_step['colour'], width=con_step['width'])
                if using_ray: operated.count.remote()
                else: operated.count()

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
            img.paste(i, (int(x-i.width/2), int(y-i.height/2)), i)
        else:
            p_log(f"Text {processed}/{len(text_list)} skipped")
        dont_cross.append(current_box_coords)
    if using_ray: operated.count.remote()
    else: operated.count()
    
    #tileReturn[tile_coords] = im
    if save_images:
        img.save(f'{save_dir}{tile_coords}.png', 'PNG')

    p_log("Rendered")

    return {tile_coords: img}