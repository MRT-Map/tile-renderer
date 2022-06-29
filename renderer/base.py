from __future__ import annotations

import os
import pickle
from pathlib import Path

import psutil
from PIL import Image
import time
import glob
import re
import blessed
from rich.progress import track

import renderer.internals.internal as internal
import renderer.validate as validate
import renderer.internals.rendering as rendering
from renderer.internals.logger import log
from renderer.objects.components import ComponentList, Component
from renderer.objects.nodes import NodeList
from renderer.objects.skin import Skin, _TextObject
from renderer.objects.zoom_params import ZoomParams
from renderer.types import RealNum, TileCoord

import renderer.tools.components as tools_component_json
import renderer.tools.line as tools_line
import renderer.tools.nodes as tools_nodes
import renderer.tools.tile as tools_tile

class _MultiprocessingOperatedHandler:
    def __init__(self, m):
        self.operated = m.Value('i', 0)

    def get(self):
        return self.operated.value

    def count(self):
        self.operated.value += 1
        
_path_in_tmp = lambda file: Path(__file__).parent/"tmp"/file

def merge_tiles(images: Path | dict[TileCoord, Image],
                save_images: bool=True,
                save_dir: Path = Path.cwd(),
                zoom: list[int] | None = None) -> dict[int, Image.Image]:
    """
    Merges tiles rendered by :py:func:`render`.

    :param images: Give in the form of ``(tile coord): (PIL Image)``, like the return value of :py:func:`render`, or as a path to a directory.
    :type images: Path | dict[TileCoord, Image]
    :param bool save_images: whether to save the tile images in a folder or not
    :param Path save_dir: the directory to save tiles in
    :param zoom: if left empty, automatically calculates all zoom values based on tiles; otherwise, the layers of zoom to merge.
    :type zoom: list[int] | None

    :returns: Given in the form of ``(Zoom): (PIL Image)``
    :rtype: dict[int, Image.Image]
    """
    if zoom is None: zoom = []
    term = blessed.Terminal()
    image_dict = {}
    tile_return = {}
    if isinstance(images, Path):
        print(term.green("Retrieving images..."), end="\r")
        for d in glob.glob(str(images/"*.png")):
            regex = re.search(r"(-?\d+, -?\d+, -?\d+)\.png$", d) # pylint: disable=anomalous-backslash-in-string
            if regex is None:
                continue
            coord = TileCoord(*internal._str_to_tuple(regex.group(1)))
            i = Image.open(d)
            image_dict[coord] = i
            with term.location(): print(term.green("Retrieving images... ") + f"Retrieved {coord}", end=term.clear_eos+"\r")
    else:
        image_dict = images
    print(term.green("\nAll images retrieved"))
    print(term.green("Determined zoom levels..."), end=" ")
    if not zoom:
        zoom = list({c.z for c in image_dict.keys()})
    print(term.green("determined"))
    for z in zoom:
        print(term.green(f"Zoom {z}: ") + "Determining tiles to be merged", end=term.clear_eos+"\r")
        to_merge = {k: v for k, v in image_dict.items() if k.z == z}

        tile_coords = list(to_merge.keys())
        x_max, x_min, y_max, y_min = tools_tile.find_ends(tile_coords)
        tile_size = list(image_dict.values())[0].size[0]
        print(term.green(f"Zoom {z}: ") + f"Creating image {tile_size*(x_max-x_min+1)}x{tile_size*(y_max-y_min+1)}", end=term.clear_eos + "\r")
        i = Image.new('RGBA', (tile_size*(x_max-x_min+1), tile_size*(y_max-y_min+1)), (0, 0, 0, 0))
        px = 0
        py = 0
        merged = 0
        start = time.time() * 1000
        for x in range(x_min, x_max+1):
            for y in range(y_min, y_max+1):
                if TileCoord(z, x, y) in to_merge.keys():
                    i.paste(to_merge[TileCoord(z, x, y)], (px, py))
                    merged += 1
                    with term.location(): print(term.green(f"Zoom {z}: ")
                                                + f"{internal._percentage(merged, len(to_merge.keys()))}% | "
                                                + f"{internal._ms_to_time(internal._time_remaining(start, merged, len(to_merge.keys())))} left | "
                                                + term.bright_black(f"Pasted {z}, {x}, {y}"), end=term.clear_eos+"\r")
                py += tile_size
            px += tile_size
            py = 0
        #tile_return[tile_components] = im
        if save_images:
            print(term.green(f"Zoom {z}: ") + "Saving image", end=term.clear_eos+"\r")
            i.save(save_dir/f'merge_{z}.png', 'PNG')
        tile_return[z] = i

    print(term.green("\nAll merges complete"))
    return tile_return

def _remove_unknown_component_types(components: ComponentList, skin: Skin) -> list[str]:
    remove_list: list[str] = []
    for component in components.component_values():
        if component.type not in skin.order:
            remove_list.append(component.name)
    for component_name in remove_list:
        del components.components[component_name]
    return remove_list

def _sort_by_tiles(tiles: list[TileCoord], components: ComponentList,
                   nodes: NodeList, zoom: ZoomParams) -> dict[TileCoord, list[Component]]:
    tile_list: dict[TileCoord, list[Component]] = {}
    for tile in tiles:
        tile_list[tile] = []
    for component in components.component_values():
        coords = tools_nodes.to_coords(component.nodes, nodes)
        rendered_in = tools_line.to_tiles(coords, zoom.min, zoom.max, zoom.range)
        for tile in rendered_in:
            if tile in tile_list.keys():
                tile_list[tile].append(component)
    return tile_list


def _process_tiles(tile_list: dict[TileCoord, list[Component]], skin: Skin) -> dict[TileCoord, list[list[Component]]]:
    grouped_tile_list: dict[TileCoord, list[list[Component]]] = {}
    for tile_coord, tile_components in track(tile_list.items(), description="Processing tiles"):
        # sort components in tiles by layer
        new_tile_components: dict[float, list[Component]] = {}
        for component in tile_components:
            if component.layer not in new_tile_components.keys():
                new_tile_components[component.layer] = []
            new_tile_components[component.layer].append(component)

        # sort components in layers in files by type
        new_tile_components = {layer: sorted(component_list, key=lambda x: skin.order.index(x.type))
                               for layer, component_list in new_tile_components.items()}

        # merge layers
        tile_components = []
        layers = sorted(new_tile_components.keys())
        for layer in layers:
            for component in new_tile_components[layer]:
                tile_components.append(component)

        # groups components of the same type if "road" tag present
        newer_tile_components: list[list[Component]] = [[]]
        # keys = list(tile_list[tile_components].keys())
        # for i in range(len(tile_list[tile_components])):
        for i, component in enumerate(tile_components):
            newer_tile_components[-1].append(component)
            if i != len(tile_components) - 1 \
                    and (tile_components[i + 1].type != component.type
                         or "road" not in skin[component.type].tags):
                newer_tile_components.append([])

        grouped_tile_list[tile_coord] = newer_tile_components

    return grouped_tile_list

def prepare_render(components: ComponentList,
                   nodes: NodeList,
                   zoom: ZoomParams,
                   export_id: str,
                   skin: Skin = Skin.from_name("default"),
                   tiles: list[TileCoord] | None = None,
                   offset: tuple[RealNum, RealNum] = (0, 0)) -> dict[TileCoord, list[list[Component]]]:
    # offset
    for node in nodes.node_values():
        node.x += offset[0]
    node.y += offset[1]

    log.info("Finding tiles...")
    # finds which tiles to render
    if tiles is not None:
        validate.v_tile_coords(tiles, zoom.min, zoom.max)
    else:  # finds box of tiles
        tiles = tools_component_json.rendered_in(components, nodes, zoom.min, zoom.max, zoom.range)

    log.info("Removing components with unknown type...")
    remove_list = _remove_unknown_component_types(components, skin)
    if remove_list:
        log.warning("The following components were removed:" + " | ".join(remove_list))

    log.info("Sorting components by tiles...")
    tile_list = _sort_by_tiles(tiles, components, nodes, zoom)

    grouped_tile_list = _process_tiles(tile_list, skin)

    for coord, grouped_components in track(grouped_tile_list.items(), description="Dumping data"):
        with open(_path_in_tmp(f"{export_id}_{coord}.0.pkl"), "wb") as f:
            pickle.dump(grouped_components, f)

    return grouped_tile_list

def _count_num_rendering_oprs(export_id: str,
                              skin: Skin,
                              zoom: ZoomParams) -> int:
    grouped_tile_list = {}
    for file in track(glob.glob(str(_path_in_tmp("*.0.pkl"))), description="Loading data"):
        with open(file, "rb") as f:
            result = re.search(fr"\b{re.escape(export_id)}_(-?\d+), (-?\d+), (-?\d+)\.0\.pkl$", file)
            grouped_tile_list[TileCoord(int(result.group(1)), int(result.group(2)), int(result.group(3)))] \
                = pickle.load(f)

    operations = 0
    op_tiles = {}
    tile_operations = 0
    for tile_coord, tile_components in track(grouped_tile_list.items(), description="Counting operations"):
        if not tile_components:
            op_tiles[tile_coord] = 0
            continue

        for group in tile_components:
            if not group: continue
            info = skin.types[group[0].type]
            for step in info[zoom.max - tile_coord.z]:
                operations += len(group)
                tile_operations += len(group)
                if info.shape == "line" and "road" in info.tags and step.layer == "back":
                    operations += 1
                    tile_operations += 1

        op_tiles[tile_coord] = tile_operations
        tile_operations = 0
    return operations

class _RayOperatedHandler:
    def __init__(self):
        self.tally = []

    def get(self):
        return len(self.tally)

    def count(self, i_=1):
        self.tally.append(i_)

def _pre_draw_components(operated,
                         operations: int,
                         start: RealNum,
                         export_id: str,
                         tile_coord: TileCoord,
                         all_components: ComponentList,
                         nodes: NodeList,
                         skin: Skin,
                         zoom: ZoomParams,
                         assets_dir: Path,
                         using_ray: bool = False,
                         debug: bool = False) -> tuple[TileCoord, list[_TextObject]] | None:
    path = _path_in_tmp(f"{export_id}_{tile_coord}.0.pkl")
    with open(path, "rb") as f:
        tile_components = pickle.load(f)
    result = rendering._draw_components(operated,
                                        operations,
                                        start,
                                        tile_coord,
                                        tile_components,
                                        all_components,
                                        nodes,
                                        skin,
                                        zoom,
                                        assets_dir,
                                        export_id,
                                        using_ray,
                                        debug)
    os.remove(path)
    if result is not None:
        with open(_path_in_tmp(f"{export_id}_{tile_coord}.1.pkl")) as f:
            pickle.dump({result[0]: result[1]}, f)
    return result


def render_part1_ray(components: ComponentList,
                     nodes: NodeList,
                     zoom: ZoomParams,
                     export_id: str,
                     skin: Skin = Skin.from_name("default"),
                     assets_dir: Path = Path(__file__).parent/"skins"/"assets",
                     processes: int = psutil.cpu_count(),
                     debug: bool = False) -> dict[TileCoord, list[_TextObject]]:
    import ray
    ray.init(num_cpus=processes)

    tile_coords = []
    for file in track(glob.glob(str(_path_in_tmp(f"{glob.escape(export_id)}_*.0.pkl"))), description="Loading tile coords"):
        re_result = re.search(fr"_(-?\d+), (-?\d+), (-?\d+)\.0\.pkl$", file)
        tile_coords.append(TileCoord(int(re_result.group(1)), int(re_result.group(2)), int(re_result.group(3))))

    operations = _count_num_rendering_oprs(export_id, skin, zoom)

    operated = ray.remote(_RayOperatedHandler).remote()

    start = time.time() * 1000
    log.info("Rendering components...")
    futures = [ray.remote(rendering._draw_components).remote(operated,
                                                             operations - 1,
                                                             start,
                                                             export_id,
                                                             tile_coord,
                                                             components,
                                                             nodes,
                                                             skin,
                                                             zoom,
                                                             assets_dir,
                                                             True,
                                                             debug)
               for tile_coord in tile_coords]
    result: list[tuple[TileCoord, list[_TextObject]] | None] = ray.get(futures)
    return {r[0]: r[1] for r in result if r is not None}

def render_part2(export_id: str) -> tuple[dict[TileCoord, list[_TextObject]], int]:
    term = blessed.Terminal()
    
    in_ = {}
    for file in track(glob.glob(str(_path_in_tmp(f"{glob.escape(export_id)}_*.1.pkl"))), description="Loading data"):
        with open(file, "rb") as f:
            in_.update(pickle.load(f))

    new_texts = rendering._prevent_text_overlap(in_)
    total_texts = sum(len(t[1]) for t in new_texts)
    with open(_path_in_tmp(f"{export_id}.2.pkl"), "wb") as f:
        pickle.dump((new_texts, total_texts), f)
    return new_texts, total_texts

def render_part3_ray(export_id: str,
                     skin: Skin = Skin.from_name("default"),
                     save_images: bool = True,
                     save_dir: Path = Path.cwd()) -> dict[TileCoord, Image.Image]:
    import ray

    with open(_path_in_tmp(f"{export_id}.2.pkl"), "rb") as f:
        new_texts, total_texts = pickle.load(f)

    log.info(f"Rendering images...")
    start = time.time() * 1000
    operated = ray.remote(_RayOperatedHandler).remote()
    futures = [ray.remote(rendering._draw_text).remote(operated,
                                                       total_texts + len(new_texts),
                                                       start,
                                                       tile_coord,
                                                       text_list,
                                                       save_images,
                                                       save_dir,
                                                       skin,
                                                       export_id,
                                                       True) for tile_coord, text_list in new_texts.items()]
    preresult = ray.get(futures)

    result = {}
    for i in preresult:
        if i is None:
            continue
        k, v = list(i.items())[0]
        result[k] = v

    for file in track(glob.glob(str(Path(__file__).parent / f'tmp/{glob.escape(export_id)}_*.tmp.png')),
                      description="Cleaning up"):
        os.remove(file)
    log.info("Render complete")

    return result


def render(components: ComponentList,
           nodes: NodeList,
           zoom: ZoomParams,
           skin: Skin = Skin.from_name("default"),
           export_id: str = "unnamed",
           save_images: bool = True,
           save_dir: Path = Path.cwd(),
           assets_dir: Path = Path(__file__).parent/"skins"/"assets",
           processes: int = psutil.cpu_count(),
           tiles: list[TileCoord] | None = None,
           offset: tuple[RealNum, RealNum] = (0, 0),
           debug: bool = False) -> dict[TileCoord, Image.Image]:
    # noinspection GrazieInspection
    """
        Renders tiles from given coordinates and zoom values.

        .. warning::
            Run this function under ``if __name__ == "__main__"`` if ``use_ray`` is False, or else there would be a lot of multiprocessing RuntimeErrors.

        :param ComponentList components: a JSON of components
        :param NodeList nodes: a JSON of nodes
        :param ZoomParams zoom: a ZoomParams object
        :param Skin skin: The skin to use for rendering the tiles
        :param str export_id: The name of the rendering task
        :param int save_images: whether to save the tile images in a folder or not
        :param Path save_dir: the directory to save tiles in
        :param Path assets_dir: the asset directory for the skin
        :param int processes: The amount of processes to run for rendering
        :param tiles: a list of tiles to render
        :type tiles: list[TileCoord] | None
        :param offset: the offset to shift all node coordinates by, given as ``(x,y)``
        :type offset: tuple[RealNum, RealNum]
        :param bool debug: Enables debugging information that is printed onto the tiles

        :returns: Given in the form of ``{tile_coord: image}``
        :rtype: dict[TileCoord, Image.Image]
        """
    prepare_render(components, nodes, zoom, export_id, skin, tiles, offset, logs=not debug)

    render_part1_ray(components, nodes, zoom, export_id, skin, assets_dir, processes, debug)
    render_part2(export_id)
    return render_part3_ray(export_id, skin, save_images, save_dir)