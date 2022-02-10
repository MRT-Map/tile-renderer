from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Any

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


def _draw_components(operated, operations: int, start: RealNum, tile_coord: TileCoord, tile_components: list[list[Component]],
                     all_components: ComponentList, nodes: NodeList, skin: Skin, max_zoom: int, max_zoom_range: RealNum,
                     assets_dir: Path, using_ray: bool=False) -> tuple[TileCoord, Image.Image, list[_TextObject]] | None:
    logger = _Logger(using_ray, operated, operations, start, tile_coord)
    if tile_components == [[]]:
        logger.log("Render complete")
        return None

    logger.log("Initialising canvas")
    size = max_zoom_range * 2 ** (max_zoom - tile_coord[0])
    img = Image.new(mode="RGBA", size=(skin.tile_size,)*2, color=skin.background)
    imd = ImageDraw.Draw(img)
    text_list: list[_TextObject] = []
    points_text_list: list[_TextObject] = []

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
                step.render(*args[type_info.shape][step.layer])

                if using_ray:
                    operated.count.remote()
                else:
                    operated.count()

            if type_info.shape == "line" and "road" in type_info.tags and step.layer == "back":
                logger.log("Rendering studs")
                con_nodes: list[str] = list(chain(*(component.nodes for component in group)))
                connected: list[tuple[Component, int]] = list(chain(*(tools.nodes.find_components_attached(x, all_components) for x in con_nodes)))
                for con_component, index in connected:
                    if "road" not in skin[con_component.type].tags:
                        continue
                    con_info = skin[con_component.type]
                    for con_step in con_info[max_zoom-tile_coord.z]:
                        if con_step.layer in ["back", "text"]:
                            continue

                        con_coords = _node_list_to_image_coords(con_component.nodes, nodes,
                                                                skin, tile_coord, size)

                        con_img = Image.new("RGBA", (skin.tile_size,)*2, (0,)*4)
                        con_imd = ImageDraw.Draw(con_img)
                        con_step: Skin.ComponentTypeInfo.LineFore
                        con_step.render(con_imd, con_coords)

                        con_mask_img = Image.new("RGBA", (skin.tile_size,)*2, (0,)*4)
                        con_mask_imd = ImageDraw.Draw(con_mask_img)
                        con_mask_imd.ellipse((con_coords[index].x - (max(con_step.width, step.width) + 2) / 2 + 1,
                                              con_coords[index].y - (max(con_step.width, step.width) + 2) / 2 + 1,
                                              con_coords[index].x + (max(con_step.width, step.width) + 2) / 2,
                                              con_coords[index].y + (max(con_step.width, step.width) + 2) / 2),
                                             fill="#000000")

                        inter = Image.new("RGBA", (skin.tile_size,)*2, (0,)*4)
                        inter.paste(con_img, (0, 0), con_mask_img)
                        img.paste(inter, (0, 0), inter)

                if using_ray:
                    operated.count.remote()
                else:
                    operated.count()

    text_list += points_text_list
    text_list.reverse()
    return tile_coord, img, text_list

def _prevent_text_overlap(texts: list[tuple[TileCoord, Image.Image, list[_TextObject]]]) -> list[tuple[TileCoord, Image.Image, list[_TextObject]]]:
    imgs: dict[TileCoord, Image.Image] = {tile_coord: img for tile_coord, img, _ in texts}
    preout = {}
    for z in list(set(c[0].z for c in texts)):
        text_dict: dict[_TextObject, list[TileCoord]] = {}
        for tile_coord, _, text_objects in texts:
            if tile_coord.z != z: continue
            for text in text_objects:
                if text not in text_dict: text_dict[text] = []
                text_dict[text].append(tile_coord)
        no_intersect: list[list[Coord]] = []
        is_rendered = True
        for text in text_dict.copy().keys():
            r = lambda a, b: mathtools.rotate_around_pivot(a, b, text.x, text.y, text.rot)
            current_box_coords = [
                r(text.x-text.w/2, text.y-text.h/2),
                r(text.x-text.w/2, text.y+text.h/2),
                r(text.x+text.w/2, text.y+text.h/2),
                r(text.x+text.w/2, text.y-text.h/2),
                r(text.x-text.w/2, text.y-text.h/2),
            ]
            for other in no_intersect:
                if mathtools.poly_intersect(current_box_coords, other):
                    is_rendered = False
                    del text_dict[text]
                    break
            no_intersect.append(current_box_coords)
            if not is_rendered: break
        for text, tile_coords in text_dict.items():
            for tile_coord in tile_coords:
                if tile_coord not in preout:
                    preout[tile_coord] = (imgs[tile_coord], [])
                preout[tile_coord][1].append(text)
    for tile_coord, _, _ in texts:
        if tile_coord not in preout: preout[tile_coord] = (imgs[tile_coord], [])
    out = [(tile_coord, img, text_objects) for tile_coord, (img, text_objects) in preout.items()]
    return out


def _draw_text(operated, operations: int, start: RealNum, image: Image.Image, tile_coord: TileCoord, text_list: list[_TextObject],
               save_images: bool, save_dir: Path, using_ray: bool=False) -> dict[TileCoord, Image.Image]:
    logger = _Logger(using_ray, operated, operations, start, tile_coord)
    processed = 0
    #print(text_list)
    for text in text_list:
        """i = text.image; x = text.x; y = text.y; w = text.w; h = text.h; rot = text.rot
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
                break"""
        processed += 1
        logger.log(f"Text {processed}/{len(text_list)} pasted")
        image.paste(text.image, (int(text.x-text.image.width/2), int(text.y-text.image.height/2)), text.image)
    for _ in range(2):
        if using_ray: operated.count.remote()
        else: operated.count()
    
    #tileReturn[tile_coord] = im
    if save_images:
        image.save(save_dir/f'{tile_coord}.png', 'PNG')

    logger.log("Rendered")

    return {tile_coord: image}