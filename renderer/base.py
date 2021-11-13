from typing import Optional
from PIL import Image
import time
import glob
import re
import multiprocessing
import sys
import blessed
import os

import renderer.internals.internal as internal
import renderer.validate as validate
import renderer.internals.rendering as rendering
import renderer.misc as misc
from renderer.types import *

import renderer.tools.component_json as tools_component_json
import renderer.tools.line as tools_line
import renderer.tools.nodes as tools_nodes
import renderer.tools.tile as tools_tile
import renderer.tools.geo_json as tools_geo_json

def tile_merge(images: Union[str, Dict[str, Image.Image]], save_images: bool=True, save_dir: str="tiles/",
               zoom: Optional[List[int]]=None) -> Dict[str, Image.Image]:
    """
    Merges tiles rendered by renderer.render().
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#tileMerge
    """
    if zoom is None: zoom = []
    term = blessed.Terminal()
    image_dict = {}
    tile_return = {}
    if isinstance(images, str):
        print(term.green("Retrieving images..."), end="\r")
        for d in glob.glob(glob.escape(images)+"*.png"):
            regex = re.search(r"(-?\d+, -?\d+, -?\d+)\.png$", d) # pylint: disable=anomalous-backslash-in-string
            if regex is None:
                continue
            coord = regex.group(1)
            i = Image.open(d)
            image_dict[coord] = i
            with term.location(): print(term.green("Retrieving images... ") + f"Retrieved {coord}", end=term.clear_eos+"\r")
    else:
        image_dict = images
    print(term.green("\nAll images retrieved"))
    print(term.green("Determined zoom levels..."), end=" ")
    if not zoom:
        for c in image_dict.keys():
            z = internal._str_to_tuple(c)[0]
            if z not in zoom:
                zoom.append(z)
    print(term.green("determined"))
    for z in zoom:
        print(term.green(f"Zoom {z}: ") + "Determining tiles to be merged", end=term.clear_eos+"\r")
        to_merge = {}
        for c, i in image_dict.items():
            if internal._str_to_tuple(c)[0] == z:
                to_merge[c] = i

        tile_coords = [internal._str_to_tuple(s) for s in to_merge.keys()]
        x_max, x_min, y_max, y_min = tools_tile.find_ends(tile_coords)
        tile_size = list(image_dict.values())[0].size[0]
        i = Image.new('RGBA', (tile_size*(x_max-x_min+1), tile_size*(y_max-y_min+1)), (0, 0, 0, 0))
        px = 0
        py = 0
        merged = 0
        start = time.time() * 1000
        for x in range(x_min, x_max+1):
            for y in range(y_min, y_max+1):
                if f"{z}, {x}, {y}" in to_merge.keys():
                    i.paste(to_merge[f"{z}, {x}, {y}"], (px, py))
                    merged += 1
                    with term.location(): print(term.green(f"Zoom {z}: ")
                                                + f"{internal._percentage(merged, len(to_merge.keys()))}% |"
                                                + f"{internal.ms_to_time(internal._time_remaining(start, merged, len(to_merge.keys())))} left | "
                                                + term.bright_black(f"Pasted {z}, {x}, {y}"), end=term.clear_eos+"\r")
                py += tile_size
            px += tile_size
            py = 0
        #tile_return[tile_components] = im
        if save_images:
            print(term.green(f"Zoom {z}: ") + "Saving image", end=term.clear_eos+"\r")
            i.save(f'{save_dir}merge_{z}.png', 'PNG')
        tile_return[str(z)] = i

    print(term.green("\nAll merges complete"))
    return tile_return

def render(component_json: ComponentJson, node_json: NodeJson, min_zoom: int, max_zoom: int, max_zoom_range: RealNum,
           skin: str='default', save_images: bool=True, save_dir: str= "", assets_dir: str= os.path.dirname(__file__) + "/skins/assets/",
           processes: int=1, tiles: Optional[List[TileCoord]]=None, offset: Tuple[RealNum, RealNum]=(0, 0)) -> Dict[str, Image.Image]:
    """
    Renders tiles from given coordinates and zoom values.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.render
    """
    if max_zoom < min_zoom:
        raise ValueError("Max zoom value is greater than min zoom value")
    term = blessed.Terminal()

    skin_json = misc.get_skin(skin)

    # validation
    print(term.green("Validating skin..."), end=" ")
    validate.v_skin_json(skin_json)
    print(term.green("validated\nValidating nodes..."), end=" ")
    validate.v_node_json(node_json)
    print(term.green("validated\nValidating components..."), end=" ")
    validate.v_component_json(component_json, node_json)

    # offset
    for node in node_json.keys():
        node_json[node]['x'] += offset[0]
        node_json[node]['y'] += offset[1]

    print(term.green("validated\nFinding tiles..."), end=" ")
    #finds which tiles to render
    if tiles is not None:
        validate.v_tile_coords(tiles, min_zoom, max_zoom)
    else: #finds box of tiles
        tiles = tools_component_json.rendered_in(component_json, node_json, min_zoom, max_zoom, max_zoom_range)

    print(term.green("found\nRemoving components with unknown type..."), end=" ")
    # remove components whose type is not in skin
    remove_list = []
    for component in component_json.keys():
        if not component_json[component]['type'].split(' ')[0] in skin_json['order']:
            remove_list.append(component)
    for component in remove_list:
        del component_json[component]
    print(term.green("removed"))
    if remove_list:
        print(term.yellow('The following components were removed:'))
        print(term.yellow(" | ".join(remove_list)))

    print(term.green("Sorting components by tiles..."), end=" ")
    #sort components by tiles
    tile_list = {}
    for tile in tiles:
        tile_list[internal._tuple_to_str(tile)] = {}
    for component in component_json.keys():
        coords = tools_nodes.to_coords(component_json[component]['nodes'], node_json)
        rendered_in = tools_line.to_tiles(coords, min_zoom, max_zoom, max_zoom_range)
        for tile in rendered_in:
            if internal._tuple_to_str(tile) in tile_list.keys():
                tile_list[internal._tuple_to_str(tile)][component] = component_json[component]

    process_start = time.time() * 1000
    processed = 0
    timeLeft = 0.0
    l = lambda processed_count, time_left, tile_components_, msg: \
        term.green(f"{internal._percentage(processed_count, len(tile_list))}% | {internal.ms_to_time(time_left)} left | ") \
        + f"{tile_components_}: " + term.bright_black(msg) + term.clear_eos
    print(term.green("sorted\n")+term.bright_green("Starting processing"))
    for tile_components in tile_list.keys():
        #sort components in tiles by layer
        new_tile_components = {}
        for component in tile_list[tile_components].keys():
            if not str(float(tile_list[tile_components][component]['layer'])) in new_tile_components.keys():
                new_tile_components[str(float(tile_list[tile_components][component]['layer']))] = {}
            new_tile_components[str(float(tile_list[tile_components][component]['layer']))][component] = tile_list[tile_components][component]
        with term.location(): print(l(processed, timeLeft, tile_components, "Sorted component by layer"), end="\r")

        #sort components in layers in files by type
        for layer in new_tile_components.keys():
            #print(new_tile_components[layer].items())
            new_tile_components[layer] = {k: v for k, v in sorted(new_tile_components[layer].items(),
                                                                  key=lambda x: skin_json['order'].index(x[1]['type'].split(' ')[0]))}
        with term.location(): print(l(processed, timeLeft, tile_components, "Sorted component by type"), end="\r")

        #merge layers
        tile_list[tile_components] = {}
        layers = sorted(new_tile_components.keys(), key=lambda x: float(x))
        for layer in layers:
            for key, component in new_tile_components[layer].items():
                tile_list[tile_components][key] = component
        with term.location(): print(l(processed, timeLeft, tile_components, "Merged layers"), end="\r")

        #groups components of the same type if "road" tag present
        newer_tile_components = [{}]
        keys = list(tile_list[tile_components].keys())
        for i in range(len(tile_list[tile_components])):
            newer_tile_components[-1][keys[i]] = tile_list[tile_components][keys[i]]
            if i != len(keys)-1 \
               and (tile_list[tile_components][keys[i + 1]]['type'].split(' ')[0] != tile_list[tile_components][keys[i]]['type'].split(' ')[0]
               or "road" not in skin_json['types'][tile_list[tile_components][keys[i]]['type'].split(' ')[0]]['tags']):
                newer_tile_components.append({})
        tile_list[tile_components] = newer_tile_components
        with term.location(): print(l(processed, timeLeft, tile_components, "Components grouped"), end="\r")

        processed += 1
        timeLeft = internal._time_remaining(process_start, processed, len(tile_list))
        #time_left = round(((int(round(time.time() * 1000)) - process_start) / processed * (len(tile_list) - processed)), 2)

    print(term.green("100.00% | 0.0s left | ") + "Processing complete" + term.clear_eos)

    #count # of rendering operations
    print(term.bright_green("Counting no. of operations"))
    operations = 0
    op_tiles = {}
    tile_operations = 0
    for tile_components in tile_list.keys():
        if tile_list[tile_components] == [{}]:
            op_tiles[tile_components] = 0
            continue

        for group in tile_list[tile_components]:
            info = skin_json['types'][list(group.values())[0]['type'].split(" ")[0]]
            style = []
            for zoom in info['style'].keys():
                if max_zoom-internal._str_to_tuple(zoom)[1] <= internal._str_to_tuple(tile_components)[0] <= max_zoom-internal._str_to_tuple(zoom)[0]:
                    style = info['style'][zoom]
                    break
            for step in style:
                for _, component in group.items():
                    operations += 1
                    tile_operations += 1
                if info['type'] == "line" and "road" in info['tags'] and step['layer'] == "back":
                    operations += 1
                    tile_operations += 1
        operations += 2
        tile_operations += 2 #text

        op_tiles[tile_components] = tile_operations
        tile_operations = 0
        print(f"Counted {tile_components}", end=term.clear_eos + "\r")

    #render
    render_start = time.time() * 1000
    print(term.bright_green("\nStarting render"))
    if __name__ == 'renderer.base':
        m = multiprocessing.Manager()
        operated = m.Value('i', 0)
        lock = m.Lock() # pylint: disable=no-member

        input_ = []
        for i in tile_list.keys():
            input_.append((lock, operated, render_start, i, tile_list[i], operations, component_json, node_json, skin_json, min_zoom, max_zoom, max_zoom_range, save_images, save_dir, assets_dir))
        p = multiprocessing.Pool(processes)
        try:
            preresult = p.map(rendering.tiles, input_)
        except KeyboardInterrupt:
            p.terminate()
            sys.exit()
        result = {}
        for i in preresult:
            if i is None:
                continue
            k, v = list(i.items())[0]
            result[k] = v

        print(term.green("100.00% | 0.0s left | ") + "Rendering complete" + term.clear_eos)
    print(term.bright_green("Render complete"))
    return result