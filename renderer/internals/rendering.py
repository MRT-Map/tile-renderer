from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any

import blessed
from PIL import Image, ImageDraw

import renderer.internals.internal as internal
import renderer.mathtools as mathtools
import renderer.tools as tools
from renderer.objects.components import ComponentList, Component
from renderer.objects.nodes import NodeList
from renderer.objects.skin import Skin, _TextObject, _node_list_to_image_coords
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

                args = {
                    "point": {
                        "circle": (imd, coords),
                        "text": (imd, coords, component.displayname, assets_dir, points_text_list),
                        "square": (imd, coords),
                        "image": (img, coords, assets_dir)
                    },
                    "line": {
                        "text": (imd, coords, assets_dir, component, text_list),
                        "back": (imd, coords),
                        "fore": (imd, coords)
                    },
                    "area": {
                        "bordertext": (imd, coords, component, assets_dir, text_list),
                        "centertext": (imd, coords, component, assets_dir, text_list),
                        "fill": (imd, img, coords, component, nodes, tile_coord, size),
                        "centerimage": (img, coords, assets_dir)
                    }
                }

                if step.layer not in args[type_info.shape].keys():
                    raise KeyError(f"{step.layer} is not a valid layer")
                logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}")
                step.render(*args)

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
                    for con_step in con_info[max_zoom-tile_coord.z]:
                        if con_step.layer in ["back", "text"]:
                            continue

                        logger.log("Studs: Extracting coords")
                        con_coords = _node_list_to_image_coords(con_component.nodes, nodes,
                                                                skin, tile_coord, size)
                        #pre_con_coords = con_coords[:]

                        con_img = Image.new("RGBA", (skin.tile_size,)*2, (0,)*4)
                        con_imd = ImageDraw.Draw(con_img)
                        con_step: Skin.ComponentTypeInfo.LineFore
                        con_step.render(con_imd, coords)

                        con_mask_img = Image.new("RGBA", (skin.tile_size,)*2, (0,)*4)
                        con_mask_imd = ImageDraw.Draw(con_img)
                        con_mask_imd.ellipse((con_coords[0].x - con_step.size / 2 + 1,
                                              con_coords[0].y - con_step.size / 2 + 1,
                                              con_coords[0].x + con_step.size / 2,
                                              con_coords[0].y + con_step.size / 2),
                                             fill="#ffffff", width=con_step.width + 2)
                        img.paste(con_img, (0, 0), con_mask_img)

                        """if index == 0:
                            con_coords = [con_coords[0], con_coords[1]]
                            if con_step.dash is None:
                                con_coords[1] = Coord((con_coords[0].x + con_coords[1].x) / 2, (con_coords[0].y + con_coords[1].y) / 2)
                        elif index == len(con_coords) - 1:
                            con_coords = [con_coords[index - 1], con_coords[index]]
                            if con_step.dash is None:
                                con_coords[0] = Coord((con_coords[0].x + con_coords[1].x) / 2, (con_coords[0].y + con_coords[1].y) / 2)
                        else:
                            con_coords = [con_coords[index - 1], con_coords[index], con_coords[index + 1]]
                            if con_step.dash is None:
                                con_coords[0] = Coord((con_coords[0].x + con_coords[1].x) / 2, (con_coords[0].y + con_coords[1].y) / 2)
                                con_coords[2] = Coord((con_coords[2].x + con_coords[1].x) / 2, (con_coords[2].y + con_coords[1].y) / 2)
                        logger.log("Studs: Segment drawn")
                        if con_step.dash is None:
                            imd.line(con_coords, fill=con_step.colour, width=con_step.width, joint="curve")
                            imd.ellipse([con_coords[0].x - con_step.width / 2 + 1,
                                         con_coords[0].y - con_step.width / 2 + 1,
                                         con_coords[0].x + con_step.width / 2,
                                         con_coords[0].y + con_step.width / 2], fill=con_step.colour)
                            imd.ellipse([con_coords[-1].x - con_step.width / 2 + 1,
                                         con_coords[-1].y - con_step.width / 2 + 1,
                                         con_coords[-1].x + con_step.width / 2,
                                         con_coords[-1].y + con_step.width / 2], fill=con_step.colour)

                        else:
                            con_offset_info = mathtools.dash_offset(pre_con_coords, con_step.dash[0],
                                                                    con_step.dash[1])[index:]
                            # print(offset_info)
                            for i, (c1, c2) in enumerate(internal._with_next(con_coords)):
                                # print(offset_info)
                                # print(c)
                                con_o, con_empty_start = con_offset_info[i]
                                for con_dash_coords in mathtools.dash(c1.x, c1.y, c2.x, c2.y,
                                                                      con_step.dash[0], con_step.dash[1], con_o,
                                                                      con_empty_start):
                                    # print(dash_coords)
                                    imd.line(con_dash_coords, fill=con_step.colour, width=con_step.width)"""
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
            for c1, c2 in internal._with_next(box):
                for d1, d2 in internal._with_next(current_box_coords):
                    can_print = False if mathtools.lines_intersect(c1.x, c1.y, c2.x, c2.y, d1.x, d1.y, d2.x, d2.y) else can_print
                    if not can_print:
                        break
                if not can_print:
                    break
            if can_print and mathtools.point_in_poly(current_box_coords[0].x, current_box_coords[0].y, box) or mathtools.point_in_poly(box[0].x, box[0].y, current_box_coords):
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
    for _ in range(2):
        if using_ray: operated.count.remote()
        else: operated.count()
    
    #tileReturn[tile_coord] = im
    if save_images:
        image.save(save_dir/f'{tile_coord}.png', 'PNG')

    logger.log("Rendered")

    return {tile_coord: image}