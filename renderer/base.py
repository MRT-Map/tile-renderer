from __future__ import annotations

from pathlib import Path

import psutil
from PIL import Image
import time
import glob
import re
import multiprocessing
import sys
import blessed

import renderer.internals.internal as internal
import renderer.validate as validate
import renderer.internals.rendering as rendering
from renderer.objects.components import ComponentList, Component
from renderer.objects.nodes import NodeList
from renderer.objects.skin import Skin, _TextObject
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
        for c in image_dict.keys():
            if c.z not in zoom:
                zoom.append(c.z)
    print(term.green("determined"))
    for z in zoom:
        print(term.green(f"Zoom {z}: ") + "Determining tiles to be merged", end=term.clear_eos+"\r")
        to_merge = {}
        for c, i in image_dict.items():
            if c.z == z:
                to_merge[c] = i

        tile_coords = list(to_merge.keys())
        x_max, x_min, y_max, y_min = tools_tile.find_ends(tile_coords)
        tile_size = list(image_dict.values())[0].size[0]
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

def render(components: ComponentList,
           nodes: NodeList,
           min_zoom: int,
           max_zoom: int,
           max_zoom_range: RealNum,
           skin: Skin = Skin.from_name("default"),
           save_images: bool = True,
           save_dir: Path = Path.cwd(),
           assets_dir: Path = Path(__file__).parent/"skins"/"assets",
           processes: int = psutil.cpu_count(),
           tiles: list[TileCoord] | None = None,
           offset: tuple[RealNum, RealNum] = (0, 0),
           use_ray: bool = True,
           debug: bool = False) -> dict[TileCoord, Image.Image]:
    # noinspection GrazieInspection
    """
        Renders tiles from given coordinates and zoom values.

        .. warning::
            Run this function under ``if __name__ == "__main__"`` if ``use_ray`` is False, or else there would be a lot of multiprocessing RuntimeErrors.

        :param ComponentList components: a JSON of components
        :param NodeList nodes: a JSON of nodes
        :param int min_zoom: minimum zoom value
        :param int max_zoom: maximum zoom value
        :param RealNum max_zoom_range: actual distance covered by a tile in the maximum zoom
        :param Skin skin: The skin to use for rendering the tiles
        :param int save_images: whether to save the tile images in a folder or not
        :param Path save_dir: the directory to save tiles in
        :param Path assets_dir: the asset directory for the skin
        :param int processes: The amount of processes to run for rendering
        :param tiles: a list of tiles to render
        :type tiles: list[TileCoord] | None
        :param offset: the offset to shift all node coordinates by, given as ``(x,y)``
        :type offset: tuple[RealNum, RealNum]
        :param bool use_ray: Whether to use Ray multiprocessing instead of the internal multiprocessing module.
        :param bool debug: Enables debugging information that is printed onto the tiles

        :returns: Given in the form of ``{tile_coord: image}``
        :rtype: dict[TileCoord, Image.Image]

        :raises ValueError: if max_zoom < min_zoom
        """

    if max_zoom < min_zoom:
        raise ValueError("Max zoom value is greater than min zoom value")
    term = blessed.Terminal()

    # offset
    for node in nodes.node_values():
        node.x += offset[0]
        node.y += offset[1]

    print(term.green("Finding tiles..."), end=" ")
    #finds which tiles to render
    if tiles is not None:
        validate.v_tile_coords(tiles, min_zoom, max_zoom)
    else: #finds box of tiles
        tiles = tools_component_json.rendered_in(components, nodes, min_zoom, max_zoom, max_zoom_range)

    print(term.green("found\nRemoving components with unknown type..."), end=" ")
    # remove components whose type is not in skin
    remove_list: list[str] = []
    for component in components.component_values():
        if component.type not in skin.order:
            remove_list.append(component.name)
    for component_name in remove_list:
        del components.components[component_name]
    print(term.green("removed"))
    if remove_list:
        print(term.yellow('The following components were removed:'))
        print(term.yellow(" | ".join(remove_list)))

    print(term.green("Sorting components by tiles..."), end=" ")
    #sort components by tiles
    tile_list: dict[TileCoord, list[Component]] = {}
    for tile in tiles:
        tile_list[tile] = []
    for component in components.component_values():
        coords = tools_nodes.to_coords(component.nodes, nodes)
        rendered_in = tools_line.to_tiles(coords, min_zoom, max_zoom, max_zoom_range)
        for tile in rendered_in:
            if tile in tile_list.keys():
                tile_list[tile].append(component)

    process_start = time.time() * 1000
    processed = 0
    l = lambda tile_components_, msg: rendering._eta(process_start, processed, len(tile_list)) \
        + f"{tile_components_}: " + term.bright_black(msg) + term.clear_eos
    print(term.green("sorted\n")+term.bright_green("Starting processing"))
    grouped_tile_list: dict[TileCoord, list[list[Component]]] = {}
    for tile_coord, tile_components in tile_list.items():
        #sort components in tiles by layer
        new_tile_components: dict[float, list[Component]] = {}
        for component in tile_components:
            if component.layer not in new_tile_components.keys():
                new_tile_components[component.layer] = []
            new_tile_components[component.layer].append(component)
        with term.location(): print(l(tile_coord, "Sorted component by layer"), end="\r")

        #sort components in layers in files by type
        new_tile_components = {layer: sorted(component_list, key=lambda x: skin.order.index(x.type))
                               for layer, component_list in new_tile_components.items()}
        with term.location(): print(l(tile_coord, "Sorted component by type"), end="\r")

        #merge layers
        tile_components = []
        layers = sorted(new_tile_components.keys())
        for layer in layers:
            for component in new_tile_components[layer]:
                tile_components.append(component)
        with term.location(): print(l(tile_coord, "Merged layers"), end="\r")

        #groups components of the same type if "road" tag present
        newer_tile_components: list[list[Component]] = [[]]
        # keys = list(tile_list[tile_components].keys())
        # for i in range(len(tile_list[tile_components])):
        for i, component in enumerate(tile_components):
            newer_tile_components[-1].append(component)
            if i != len(tile_components)-1 \
               and (tile_components[i + 1].type != component.type
               or "road" not in skin[component.type].tags):
                newer_tile_components.append([])

        grouped_tile_list[tile_coord] = newer_tile_components
        with term.location(): print(l(tile_coord, "Components grouped"), end="\r")

        processed += 1
        #time_left = round(((int(round(time.time() * 1000)) - process_start) / processed * (len(tile_list) - processed)), 2)

    print(term.green("100.00% | 0.0s left | ") + "Processing complete" + term.clear_eos)

    #count # of rendering operations for part 1
    operations = 0
    op_tiles = {}
    tile_operations = 0
    for tile_coord, tile_components in grouped_tile_list.items():
        if not tile_components:
            op_tiles[tile_coord] = 0
            continue

        for group in tile_components:
            info = skin.types[group[0].type]
            for step in info[max_zoom-tile_coord.z]:
                operations += len(group)
                tile_operations += len(group)
                if info.shape == "line" and "road" in info.tags and step.layer == "back":
                    operations += 1
                    tile_operations += 1

        op_tiles[tile_coord] = tile_operations
        tile_operations = 0
        print(f"Counted {tile_coord}", end=term.clear_eos + "\r")

    #render
    if use_ray:
        try: # noinspection PyPackageRequirements
            import ray
        except ModuleNotFoundError:
            use_ray = False

    if use_ray:
        ray.init(num_cpus=processes)

        @ray.remote
        class _RayOperatedHandler:
            def __init__(self):
                self.tally = []

            def get(self):
                return len(self.tally)

            def count(self, i_=1):
                self.tally.append(i_)

        operated = _RayOperatedHandler.remote()

        print(term.bright_green("\nRendering components..."))
        input_ = []
        start = time.time() * 1000
        for tile_coord, component_group in grouped_tile_list.items():
            input_.append((operated, operations-1, start, tile_coord, component_group, components, nodes,
                           skin, max_zoom, max_zoom_range, assets_dir, True, debug))
        futures = [ray.remote(rendering._draw_components).remote(*input_[i]) for i in range(len(input_))]
        prepreresult: list[tuple[TileCoord, Image.Image, list[_TextObject]] | None] = ray.get(futures)
        prepreresult = list(filter(lambda r: r is not None, prepreresult))

        print(term.bright_green("\nEliminating overlapping text..."))
        input_ = []
        new_texts = rendering._prevent_text_overlap(prepreresult)
        total_texts = sum(len(t[2]) for t in new_texts)

        start = time.time() * 1000
        print(term.bright_green("\nRendering text..."))
        operated = _RayOperatedHandler.remote()
        for tile_coord, image, text_list in new_texts:
            input_.append((operated, total_texts+len(new_texts), start, image, tile_coord, text_list,
                           save_images, save_dir, skin, True))
        futures = [ray.remote(rendering._draw_text).remote(*input_[i]) for i in range(len(input_))]
        preresult = ray.get(futures)

        result = {}
        for i in preresult:
            if i is None:
                continue
            k, v = list(i.items())[0]
            result[k] = v
        ray.shutdown()
    else:
        if __name__ == 'renderer.base':
            operated = _MultiprocessingOperatedHandler(multiprocessing.Manager())

            print(term.bright_green("\nRendering components..."))
            input_ = []
            start = time.time() * 1000
            for tile_coord, component_group in grouped_tile_list.items():
                input_.append((operated, operations - 1, start, tile_coord, component_group, components, nodes,
                               skin, max_zoom, max_zoom_range, assets_dir, True, debug))
            p = multiprocessing.Pool(processes)
            try:
                prepreresult = p.starmap(rendering._draw_components, input_)
                prepreresult = list(filter(lambda r: r is not None, prepreresult))
            except KeyboardInterrupt:
                p.terminate()
                sys.exit()

            print(term.bright_green("\nEliminating overlapping text..."))
            input_ = []
            new_texts = rendering._prevent_text_overlap(prepreresult)
            total_texts = sum(len(t[2]) for t in new_texts)

            start = time.time() * 1000
            print(term.bright_green("\nRendering text..."))
            operated = _MultiprocessingOperatedHandler(multiprocessing.Manager())
            for tile_coord, image, text_list in new_texts:
                input_.append((operated, total_texts + len(new_texts), start, image, tile_coord, text_list,
                               save_images, save_dir, skin, True))

            try:
                preresult = p.starmap(rendering._draw_text, input_)
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