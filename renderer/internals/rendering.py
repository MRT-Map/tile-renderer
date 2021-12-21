import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any

from PIL import Image, ImageDraw
import blessed
import re
import itertools

import renderer.internals.internal as internal
import renderer.tools as tools
import renderer.mathtools as mathtools
from renderer.objects.components import ComponentList, Component
from renderer.objects.nodes import NodeList
from renderer.objects.skin import Skin
from renderer.types import RealNum, TileCoord, Coord

term = blessed.Terminal()

try: import ray
except ModuleNotFoundError: pass

@dataclass
class _Logger:
    using_ray: bool
    operated: Any
    operations: int
    start: RealNum
    tile_coords: TileCoord

    def log(self, msg):
        if self.using_ray: ops = ray.get(self.operated.get.remote())
        else: ops = self.operated.get()
        if ops != 0 and self.operations != 0:
            print(term.green(f"{internal._percentage(ops, self.operations)}% | " +
                             f"{internal._ms_to_time(internal._time_remaining(self.start, ops, self.operations))} left | ") +
                  f"{self.tile_coords}: " + term.bright_black(msg), flush=True)
        else:
            print(term.green(f"00.0% | 0.0s left | ") + f"{self.tile_coords}: " + term.bright_black(msg), flush=True)


@dataclass
class _TextObject:
    image: Image.Image
    x: RealNum
    y: RealNum
    w: RealNum
    h: RealNum
    rot: RealNum

def _node_list_to_image_coords(node_list: List[str], nodes: NodeList, skin: Skin, tile_coord: TileCoord, size: RealNum) -> List[Coord]:
    image_coords = []
    for x, y in tools.nodes.to_coords(node_list, nodes):
        xc = x - tile_coord[1] * size
        yc = y - tile_coord[2] * size
        xs = int(skin.tile_size / size * xc)
        ys = int(skin.tile_size / size * yc)
        image_coords.append((xs, ys))
    return image_coords

def _draw_components(operated, operations: int, start: RealNum, tile_coord: TileCoord, tile_components: List[List[Component]],
                     all_components: ComponentList, nodes: NodeList, skin: Skin, max_zoom: int, max_zoom_range: RealNum,
                     assets_dir: Path, using_ray: bool=False) -> Dict[TileCoord, Tuple[Image.Image, List[_TextObject]]]:
    logger = _Logger(using_ray, operated, operations, start, tile_coord)
    if tile_components == [[]]:
        logger.log("Render complete")
        return {}

    logger.log("Initialising canvas")
    size = max_zoom_range * 2 ** (max_zoom - tile_coord[0])
    img = Image.new(mode="RGBA", size=(skin.tile_size,)*2, color=skin.background)
    imd = ImageDraw.Draw(img)
    text_list: List[_TextObject] = []
    points_text_list: List[_TextObject] = []

    for group in tile_components:
        type_info = skin[group[0].type]
        style = type_info[max_zoom-tile_coord[0]]
        for step in style:
            for component in group:
                coords = _node_list_to_image_coords(component.nodes, nodes, skin, tile_coord, size)

                def point_circle():
                    imd.ellipse((coords[0][0] - step.size / 2 + 1,
                                 coords[0][1] - step.size / 2 + 1,
                                 coords[0][0] + step.size / 2,
                                 coords[0][1] + step.size / 2),
                                fill=step.colour, outline=step.outline, width=step.width)

                def point_text():
                    font = skin.get_font("", step.size, assets_dir)
                    text_length = int(imd.textlength(component.displayname, font))
                    pt_i = Image.new('RGBA', (2 * text_length, 2 * (step.size + 4)), (0, 0, 0, 0))
                    pt_d = ImageDraw.Draw(pt_i)
                    pt_d.text((text_length, step.size + 4), component.displayname, fill=step.colour, font=font,
                              anchor="mm")
                    tw, th = pt_i.size
                    points_text_list.append(_TextObject(pt_i, coords[0][0] + step.offset[0], coords[0][1] + step.offset[1], tw, th, 0))
                    #font = skin.get_font("", step.size)
                    #img.text((coords[0][0]+step.offset[0], coords[0][1]+step.offset[1]), component.displayname, fill=step.colour, font=font, anchor=step['anchor'])

                def point_square():
                    imd.rectangle((coords[0][0] - step.size / 2 + 1,
                                   coords[0][1] - step.size / 2 + 1,
                                   coords[0][0] + step.size / 2,
                                   coords[0][1] + step.size / 2),
                                  fill=step.colour, outline=step.outline, width=step.width)

                def point_image():
                    icon = Image.open(assets_dir/step.file)
                    img.paste(icon, (int(coords[0][0] - icon.width / 2 + step.offset[0]),
                                     int(coords[0][1] - icon.height / 2 + step.offset[1])), icon)

                def line_text():
                    logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Calculating text length")
                    font = skin.get_font("", step.size, assets_dir)
                    text_length = int(imd.textlength(component.displayname, font))
                    if text_length == 0:
                        text_length = int(imd.textlength("----------", font))
                    for c in range(len(coords) - 1):
                        # print(coords)
                        # print(mathtools.line_in_box(coords, 0, skin.tile_size, 0, skin.tile_size))
                        t = math.floor(math.dist(coords[c], coords[c + 1]) / (4 * text_length))
                        t = 1 if t == 0 else t
                        if mathtools.line_in_box(coords, 0, skin.tile_size, 0, skin.tile_size) \
                                and 2 * text_length <= math.dist(coords[c], coords[c + 1]):
                            # print(mathtools.midpoint(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], step.offset))
                            logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Generating name text")
                            for tx, ty, trot in mathtools.midpoint(coords[c][0], coords[c][1], coords[c + 1][0],
                                                                   coords[c + 1][1], step.offset, n=t):
                                lt_i = Image.new('RGBA', (2 * text_length, 2 * (step.size + 4)), (0, 0, 0, 0))
                                lt_d = ImageDraw.Draw(lt_i)
                                lt_d.text((text_length, step.size + 4), component.displayname,
                                          fill=step.colour, font=font, anchor="mm")
                                tw, th = lt_i.size[:]
                                lt_i = lt_i.rotate(trot, expand=True)
                                text_list.append(_TextObject(lt_i, tx, ty, tw, th, trot))
                        if "oneWay" in component.tags and text_length <= math.dist(coords[c], coords[c + 1]):
                            logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Generating oneway arrows")
                            font = skin.get_font("b", step.size, assets_dir)
                            counter = 0
                            t = math.floor(math.dist(coords[c], coords[c + 1]) / (4 * text_length))
                            for tx, ty, _ in mathtools.midpoint(coords[c][0], coords[c][1], coords[c + 1][0],
                                                                coords[c + 1][1], step.offset, n=2 * t + 1):
                                if counter % 2 == 1:
                                    counter += 1
                                    continue
                                trot = math.degrees(
                                    math.atan2(coords[c + 1][0] - coords[c][0], coords[c + 1][1] - coords[c][1]))
                                text_length = int(imd.textlength("↓", font))
                                lt_i = Image.new('RGBA', (2 * text_length, 2 * (step.size + 4)), (0, 0, 0, 0))
                                lt_d = ImageDraw.Draw(lt_i)
                                lt_d.text((text_length, step.size + 4), "↓", fill=step.colour, font=font,
                                          anchor="mm")
                                tw, th = lt_i.size[:]
                                lt_i = lt_i.rotate(trot, expand=True)
                                text_list.append(_TextObject(lt_i, tx, ty, tw, th, trot))
                                counter += 1

                def line_backfore():
                    if step.dash is None:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Drawing line")
                        imd.line(coords, fill=step.colour, width=step.width, joint="curve")
                        if "unroundedEnds" not in type_info.tags:
                            imd.ellipse([coords[0][0] - step.width / 2 + 1, coords[0][1] - step.width / 2 + 1,
                                         coords[0][0] + step.width / 2, coords[0][1] + step.width / 2],
                                        fill=step.colour)
                            imd.ellipse([coords[-1][0] - step.width / 2 + 1, coords[-1][1] - step.width / 2 + 1,
                                         coords[-1][0] + step.width / 2, coords[-1][1] + step.width / 2],
                                        fill=step.colour)
                    else:
                        offset_info = mathtools.dash_offset(coords, step.dash[0], step.dash[1])
                        # print(offset_info)
                        for c in range(len(coords) - 1):
                            logger.log(
                                f"{style.index(step) + 1}/{len(style)} {component.name}: Drawing dashes for section {c + 1} of {len(coords)}")
                            o, empty_start = offset_info[c]
                            for dash_coords in mathtools.dash(coords[c][0], coords[c][1], coords[c + 1][0],
                                                              coords[c + 1][1], step.dash[0], step.dash[1], o,
                                                              empty_start):
                                # print(dash_coords)
                                imd.line(dash_coords, fill=step.colour, width=step.width)

                def area_bordertext():
                    logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Calculating text length")
                    font = skin.get_font("", step.size, assets_dir)
                    text_length = int(imd.textlength(component.displayname.replace('\n', ''), font))
                    for c1 in range(len(coords)):
                        c2 = c1 + 1 if c1 != len(coords) - 1 else 0
                        if mathtools.line_in_box(coords, 0, skin.tile_size, 0,
                                                 skin.tile_size) and 2 * text_length <= math.dist(coords[c1], coords[c2]):
                            # coords[c]
                            logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Midpoints calculated")
                            t = math.floor(math.dist(coords[c1], coords[c2]) / (4 * text_length))
                            t = 1 if t == 0 else t
                            all_points = mathtools.midpoint(coords[c1][0], coords[c1][1], coords[c2][0], coords[c2][1],
                                                           step.offset, n=t, return_both=True)
                            for n in range(0, len(all_points), 2):
                                logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: {component.name}: " +
                                           f"Generating text {n + 1} of {len(all_points)} in section {c1} of {len(coords) + 1}")
                                points = [all_points[n], all_points[n + 1]]
                                if step.offset < 0:
                                    tx, ty, trot = points[0] if not mathtools.point_in_poly(points[0][0], points[0][1],
                                                                                            coords) else points[1]
                                else:
                                    # print(points[0][0], points[0][1], coords)
                                    # print(mathtools.point_in_poly(points[0][0], points[0][1], coords))
                                    tx, ty, trot = points[0] if mathtools.point_in_poly(points[0][0], points[0][1],
                                                                                        coords) else points[1]
                                abt_i = Image.new('RGBA', (2 * text_length, 2 * (step.size + 4)), (0, 0, 0, 0))
                                abt_d = ImageDraw.Draw(abt_i)
                                abt_d.text((text_length, step.size + 4), component.displayname.replace('\n', ''),
                                           fill=step.colour, font=font, anchor="mm")
                                tw, th = abt_i.size[:]
                                abt_ir = abt_i.rotate(trot, expand=True)
                                text_list.append(_TextObject(abt_ir, tx, ty, tw, th, trot))

                def area_centertext():
                    logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Calculating center")
                    cx, cy = mathtools.poly_center(coords)
                    cx += step.offset[0]
                    cy += step.offset[1]
                    font = skin.get_font("", step.size, assets_dir)
                    text_length = int(min(imd.textlength(x, font) for x in component.displayname.split('\n')))

                    left = min(c[0] for c in coords)
                    right = max(c[0] for c in coords)
                    delta = right - left
                    if text_length > delta:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Breaking up string")
                        tokens = component.displayname.split()
                        wss = re.findall(r"\s+", component.displayname)
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
                        text = component.displayname
                        text_size = step.size + 4

                    act_i = Image.new('RGBA', (2 * text_length, 2 * text_size), (0, 0, 0, 0))
                    act_d = ImageDraw.Draw(act_i)
                    cw, ch = act_i.size
                    act_d.text((text_length, text_size), text, fill=step.colour, font=font, anchor="mm")
                    text_list.append(_TextObject(act_i, cx, cy, cw, ch, 0))

                def area_fill():
                    ai = Image.new("RGBA", (skin.tile_size, skin.tile_size), (0, 0, 0, 0))
                    ad = ImageDraw.Draw(ai)

                    if step.stripe is not None:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Generating stripes")
                        x_max, x_min, y_max, y_min = tools.line.find_ends(coords)
                        x_max += x_max - x_min
                        x_min -= y_max - y_min
                        y_max += x_max - x_min
                        y_min -= y_max - y_min
                        af_i = Image.new("RGBA", (skin.tile_size, skin.tile_size), (0, 0, 0, 0))
                        af_d = ImageDraw.Draw(af_i)
                        tlx = x_min - 1
                        while tlx <= x_max:
                            af_d.polygon(
                                [(tlx, y_min), (tlx + step.stripe[0], y_min), (tlx + step.stripe[0], y_max),
                                 (tlx, y_max)], fill=step.colour)
                            tlx += step.stripe[0] + step.stripe[1]
                        af_i = af_i.rotate(step.stripe[2], center=mathtools.poly_center(coords))
                        mi = Image.new("RGBA", (skin.tile_size, skin.tile_size), (0, 0, 0, 0))
                        md = ImageDraw.Draw(mi)
                        md.polygon(coords, fill=step.colour)
                        pi = Image.new("RGBA", (skin.tile_size, skin.tile_size), (0, 0, 0, 0))
                        pi.paste(af_i, (0, 0), mi)
                        ai.paste(pi, (0, 0), pi)
                    else:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Filling area")
                        ad.polygon(coords, fill=step.colour, outline=step.outline)

                    if component.hollows is not None:
                        for n in component.hollows:
                            n_coords = _node_list_to_image_coords([n], nodes, skin, tile_coord, size)
                            ad.polygon(n_coords, fill=(0, 0, 0, 0))
                    img.paste(ai, (0, 0), ai)

                    if step.outline is not None:
                        logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Drawing outline")
                        exterior_outline = coords[:]
                        exterior_outline.append(exterior_outline[0])
                        outlines = [exterior_outline]
                        if component.hollows is not None:
                            for n in component.hollows:
                                n_coords = _node_list_to_image_coords([n], nodes, skin, tile_coord, size)
                                n_coords.append(n_coords[0])
                                outlines.append(n_coords)
                        for o_coords in outlines:
                            imd.line(o_coords, fill=step.outline, width=2, joint="curve")
                            if "unroundedEnds" not in type_info.tags:
                                imd.ellipse(
                                    [o_coords[0][0] - 2 / 2 + 1, o_coords[0][1] - 2 / 2 + 1, o_coords[0][0] + 2 / 2,
                                     o_coords[0][1] + 2 / 2], fill=step.outline)

                def area_centerimage():
                    cx, cy = mathtools.poly_center(coords)
                    icon = Image.open(assets_dir/step['file'])
                    img.paste(icon, (cx + step.offset[0], cy + step.offset[1]), icon)

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

                if step.layer not in funcs[type_info.shape].keys():
                    raise KeyError(f"{step.layer} is not a valid layer")
                logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: ")
                funcs[type_info.shape][step.layer]()

                if using_ray:
                    operated.count.remote()
                else:
                    operated.count()

            if type_info.shape == "line" and "road" in type_info.tags and step.layer == "back":
                logger.log("Studs: Finding connected lines")
                con_nodes: List[str] = []
                for component in group:
                    con_nodes += component.nodes
                connected_pre = [tools.nodes.find_components_attached(x, all_components) for x in con_nodes]
                connected: List[Tuple[Component, int]] = []
                for i in connected_pre:
                    connected += i
                for con_component, index in connected:
                    if "road" not in skin[con_component.type].tags:
                        continue
                    con_info = skin[con_component.type]
                    for con_step in con_info[max_zoom-tile_coord[0]]:
                        if con_step.layer in ["back", "text"]:
                            continue

                        logger.log("Studs: Extracting coords")
                        con_coords = _node_list_to_image_coords(con_component.nodes, nodes,
                                                                skin, tile_coord, size)
                        pre_con_coords = con_coords[:]

                        logger.log("Studs: Coords processed")
                        if index == 0:
                            con_coords = [con_coords[0], con_coords[1]]
                            if con_step.dash is None:
                                con_coords[1] = ((con_coords[0][0] + con_coords[1][0]) / 2, (con_coords[0][1] + con_coords[1][1]) / 2)
                        elif index == len(con_coords) - 1:
                            con_coords = [con_coords[index - 1], con_coords[index]]
                            if con_step.dash is None:
                                con_coords[0] = ((con_coords[0][0] + con_coords[1][0]) / 2, (con_coords[0][1] + con_coords[1][1]) / 2)
                        else:
                            con_coords = [con_coords[index - 1], con_coords[index], con_coords[index + 1]]
                            if con_step.dash is None:
                                con_coords[0] = ((con_coords[0][0] + con_coords[1][0]) / 2, (con_coords[0][1] + con_coords[1][1]) / 2)
                                con_coords[2] = ((con_coords[2][0] + con_coords[1][0]) / 2, (con_coords[2][1] + con_coords[1][1]) / 2)
                        logger.log("Studs: Segment drawn")
                        if con_step.dash is None:
                            imd.line(con_coords, fill=con_step.colour, width=con_step.width, joint="curve")
                            imd.ellipse([con_coords[0][0] - con_step.width / 2 + 1,
                                         con_coords[0][1] - con_step.width / 2 + 1,
                                         con_coords[0][0] + con_step.width / 2,
                                         con_coords[0][1] + con_step.width / 2], fill=con_step.colour)
                            imd.ellipse([con_coords[-1][0] - con_step.width / 2 + 1,
                                         con_coords[-1][1] - con_step.width / 2 + 1,
                                         con_coords[-1][0] + con_step.width / 2,
                                         con_coords[-1][1] + con_step.width / 2], fill=con_step.colour)

                        else:
                            con_offset_info = mathtools.dash_offset(pre_con_coords, con_step.dash[0],
                                                                    con_step.dash[1])[index:]
                            # print(offset_info)
                            for c in range(len(con_coords) - 1):
                                # print(offset_info)
                                # print(c)
                                con_o, con_empty_start = con_offset_info[c]
                                for con_dash_coords in mathtools.dash(con_coords[c][0], con_coords[c][1],
                                                                      con_coords[c + 1][0], con_coords[c + 1][1],
                                                                      con_step.dash[0], con_step.dash[1], con_o,
                                                                      con_empty_start):
                                    # print(dash_coords)
                                    imd.line(con_dash_coords, fill=con_step.colour, width=con_step.width)
                if using_ray:
                    operated.count.remote()
                else:
                    operated.count()

    text_list += points_text_list
    text_list.reverse()
    img = img.crop((0, 0, +img.width, img.height))
    text_list = []
    return {tile_coord: (img, text_list)}

def _draw_text(operated, operations: int, start: RealNum, image: Image.Image, tile_coord: TileCoord, text_list: List[_TextObject],
               save_images: bool, save_dir: Path, using_ray: bool=False) -> Dict[TileCoord, Image.Image]:
    logger = _Logger(using_ray, operated, operations, start, tile_coord)
    dont_cross = []
    processed = 0
    #print(text_list)
    for text in text_list:
        i = text.image; x = text.x; y = text.y; w = text.w; h = text.h; rot = text.rot
        r = lambda a, b: mathtools.rotate_around_pivot(a, b, x, y, rot)
        current_box_coords = [r(x-w/2, y-h/2), r(x-w/2, y+h/2), r(x+w/2, y+h/2), r(x+w/2, y-h/2), r(x-w/2, y-h/2)]
        can_print = True
        for box in dont_cross:
            o_text = text_list[dont_cross.index(box)]
            ox = o_text.x; oy = o_text.y; ow = o_text.w; oh = o_text.h
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
            logger.log(f"Text {processed}/{len(text_list)} pasted")
            image.paste(i, (int(x-i.width/2), int(y-i.height/2)), i)
        else:
            logger.log(f"Text {processed}/{len(text_list)} skipped")
        dont_cross.append(current_box_coords)
    if using_ray: operated.count.remote()
    else: operated.count()
    
    #tileReturn[tile_coord] = im
    if save_images:
        image.save(save_dir/f'{internal._tuple_to_str(tile_coord)}.png', 'PNG')

    logger.log("Rendered")

    return {tile_coord: image}