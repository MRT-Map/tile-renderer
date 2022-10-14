from __future__ import annotations

import gc
import glob
import logging
import os
import pickle
import re
from pathlib import Path
from queue import Empty, Queue

import psutil
import ray
import vector
from PIL import Image
from rich.progress import Progress, track
from vector import Vector2D

import renderer.internals.rendering as rendering
from renderer.internals.logger import log
from renderer.types import RealNum
from renderer.types.coord import TileCoord, WorldCoord, WorldLine
from renderer.types.pla2 import Component, Pla2File
from renderer.types.skin import Skin, _TextObject
from renderer.types.zoom_params import ZoomParams


def _path_in_tmp(file: str) -> Path:
    return Path(__file__).parent / "tmp" / file


def _remove_unknown_component_types(components: Pla2File, skin: Skin) -> list[str]:
    remove_list: list[str] = []
    for component in components.components:
        if component.type not in skin.order:
            remove_list.append(component.fid)
    for component_id in remove_list:
        del components[component_id]
    return remove_list


def _sort_by_tiles(
    tiles: list[TileCoord], components: Pla2File, zoom: ZoomParams
) -> dict[TileCoord, list[Component]]:
    tile_list: dict[TileCoord, list[Component]] = {}
    for tile in tiles:
        tile_list[tile] = []
    for component in components:
        rendered_in = component.nodes.to_tiles(zoom)
        for tile in rendered_in:
            if tile in tile_list.keys():
                tile_list[tile].append(component)
    return tile_list


def _process_tiles(
    tile_list: dict[TileCoord, list[Component]], skin: Skin
) -> dict[TileCoord, list[list[Component]]]:
    grouped_tile_list: dict[TileCoord, list[list[Component]]] = {}
    for tile_coord, tile_components in track(
        tile_list.items(), description="Processing tiles"
    ):
        # sort components in tiles by layer
        new_tile_components: dict[float, list[Component]] = {}
        for component in tile_components:
            if component.layer not in new_tile_components.keys():
                new_tile_components[component.layer] = []
            new_tile_components[component.layer].append(component)

        # sort components in layers in files by type
        new_tile_components = {
            layer: sorted(component_list, key=lambda x: skin.order.index(x.type))
            for layer, component_list in new_tile_components.items()
        }

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
            if i != len(tile_components) - 1 and (
                tile_components[i + 1].type != component.type
                or "road" not in skin[component.type].tags
            ):
                newer_tile_components.append([])
        if newer_tile_components != [[]]:
            grouped_tile_list[tile_coord] = newer_tile_components

    return grouped_tile_list


def prepare_render(
    components: Pla2File,
    zoom: ZoomParams,
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    tiles: list[TileCoord] | None = None,
    offset: Vector2D = vector.obj(x=0, y=0),
) -> dict[TileCoord, list[list[Component]]]:
    log.info("Offsetting coordinates...")
    for component in components:
        component.nodes = WorldLine(
            [
                WorldCoord(coord.x + offset.x, coord.y + offset.y)
                for coord in component.nodes
            ]
        )

    if tiles is None:
        log.info("Finding tiles...")
        tiles = Component.rendered_in(components.components, zoom)

    log.info("Removing components with unknown type...")
    remove_list = _remove_unknown_component_types(components, skin)
    if remove_list:
        log.warning("The following components were removed:" + " | ".join(remove_list))

    log.info("Sorting components by tiles...")
    tile_list = _sort_by_tiles(tiles, components, zoom)

    grouped_tile_list = _process_tiles(tile_list, skin)

    for coord, grouped_components in track(
        grouped_tile_list.items(), description="Dumping data"
    ):
        with open(_path_in_tmp(f"{export_id}_{coord}.0.pkl"), "wb") as f:
            pickle.dump(grouped_components, f)

    return grouped_tile_list


def _count_num_rendering_oprs(
    export_id: str, skin: Skin, zoom: ZoomParams
) -> dict[TileCoord, int]:
    grouped_tile_list: dict[TileCoord, list[Pla2File]] = {}
    for file in track(
        glob.glob(str(_path_in_tmp(f"{glob.escape(export_id)}_*.0.pkl"))),
        description="Loading data",
    ):
        with open(file, "rb") as f:
            result = re.search(
                rf"\b{re.escape(export_id)}_(-?\d+), (-?\d+), (-?\d+)\.0\.pkl$", file
            )
            grouped_tile_list[
                TileCoord(
                    int(result.group(1)), int(result.group(2)), int(result.group(3))
                )
            ] = pickle.load(f)

    tile_operations = 0
    operations = {}
    for tile_coord, tile_components in track(
        grouped_tile_list.items(), description="Counting operations"
    ):
        if not tile_components:
            operations[tile_coord] = 0
            continue

        for group in tile_components:
            if not group:
                continue
            info = skin.types[group[0].type]
            for step in info[zoom.max - tile_coord.z]:
                tile_operations += len(group)
                if (
                    info.shape == "line"
                    and "road" in info.tags
                    and step.layer == "back"
                ):
                    tile_operations += 1

        operations[tile_coord] = tile_operations
        tile_operations = 0
    return operations


@ray.remote
class ProgressHandler:
    def __init__(self):
        self.queue = Queue()
        self.completed = 0

    def add(self, id_: TileCoord):
        self.queue.put_nowait(id_)

    def get(self) -> TileCoord:
        return self.queue.get_nowait()

    def complete(self):
        self.completed += 1

    def get_complete(self):
        return self.completed


def _pre_draw_components(
    ph: ProgressHandler,
    tile_coord: TileCoord,
    all_components: Pla2File,
    skin: Skin,
    zoom: ZoomParams,
    assets_dir: Path,
    export_id: str,
) -> tuple[TileCoord, list[_TextObject]]:
    path = _path_in_tmp(f"{export_id}_{tile_coord}.0.pkl")
    with open(path, "rb") as f:
        tile_components = pickle.load(f)
    logging.getLogger("fontTools").setLevel(logging.CRITICAL)
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    result = rendering._draw_components(
        ph,
        tile_coord,
        tile_components,
        all_components,
        skin,
        zoom,
        assets_dir,
        export_id,
    )
    os.remove(path)
    if result is not None:
        with open(_path_in_tmp(f"{export_id}_{tile_coord}.1.pkl"), "wb") as f:
            pickle.dump({result[0]: result[1]}, f)
    return result


def render_part1_ray(
    components: Pla2File,
    zoom: ZoomParams,
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    assets_dir: Path = Path(__file__).parent / "skins" / "assets",
    batch_size: int = 8,
) -> dict[TileCoord, list[_TextObject]]:
    tile_coords = []
    for file in glob.glob(str(_path_in_tmp(f"{glob.escape(export_id)}_*.0.pkl"))):
        re_result = re.search(rf"_(-?\d+), (-?\d+), (-?\d+)\.0\.pkl$", file)
        tile_coords.append(
            TileCoord(
                int(re_result.group(1)),
                int(re_result.group(2)),
                int(re_result.group(3)),
            )
        )

    operations = _count_num_rendering_oprs(export_id, skin, zoom)
    gc.collect()

    log.info(f"Rendering components in {len(tile_coords)} tiles...")
    ph = ProgressHandler.remote()
    futures = [
        ray.remote(_pre_draw_components).remote(
            ph, tile_coord, components, skin, zoom, assets_dir, export_id
        )
        for tile_coord in tile_coords[:batch_size]
    ]
    active_tasks = batch_size
    cursor = batch_size
    with Progress() as progress:
        main_id = progress.add_task(
            "Rendering components", total=sum(operations.values())
        )
        ids = {}
        progresses = {}
        while ray.get(ph.get_complete.remote()) != len(tile_coords):
            while active_tasks < batch_size and cursor < len(tile_coords):
                futures.append(
                    ray.remote(_pre_draw_components).remote(
                        ph,
                        tile_coords[cursor],
                        components,
                        skin,
                        zoom,
                        assets_dir,
                        export_id,
                    )
                )
                cursor += 1
                active_tasks += 1
            try:
                id_ = ray.get(ph.get.remote())
            except Empty:
                continue
            if id_ not in ids:
                ids[id_] = progress.add_task(str(id_), total=operations[id_])
                progresses[id_] = 0
            progress.advance(ids[id_], 1)
            progress.advance(main_id, 1)
            progresses[id_] += 1
            if operations[id_] <= progresses[id_]:
                progress.update(ids[id_], visible=False)
                progress.remove_task(ids[id_])
                del progresses[id_]
                del ids[id_]
                active_tasks -= 1
    result: list[tuple[TileCoord, list[_TextObject]]] = ray.get(futures)
    return {r[0]: r[1] for r in result}


def render_part2(export_id: str) -> tuple[dict[TileCoord, list[_TextObject]], int]:
    in_ = {}
    for file in track(
        glob.glob(str(_path_in_tmp(f"{glob.escape(export_id)}_*.1.pkl"))),
        description="Loading data",
    ):
        with open(file, "rb") as f:
            in_.update(pickle.load(f))
    new_texts = rendering._prevent_text_overlap(in_)
    total_texts = sum(len(t) for t in new_texts.values())
    with open(_path_in_tmp(f"{export_id}.2.pkl"), "wb") as f:
        pickle.dump((new_texts, total_texts), f)
    for file in track(
        glob.glob(str(_path_in_tmp(f"{glob.escape(export_id)}_*.1.pkl"))),
        description="Loading data",
    ):
        os.remove(file)
    return new_texts, total_texts


def render_part3_ray(
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    save_images: bool = True,
    save_dir: Path = Path.cwd(),
) -> dict[TileCoord, Image.Image]:
    import ray

    with open(_path_in_tmp(f"{export_id}.2.pkl"), "rb") as f:
        new_texts, total_texts = pickle.load(f)

    log.info(f"Rendering images in {len(new_texts)} tiles...")
    ph = ProgressHandler.remote()
    futures = [
        ray.remote(rendering._draw_text).remote(
            ph, tile_coord, text_list, save_images, save_dir, skin, export_id
        )
        for tile_coord, text_list in track(
            new_texts.items(), description="Dispatching tasks"
        )
    ]
    with Progress() as progress:
        main_id = progress.add_task(
            "Rendering texts", total=sum(len(l) for l in new_texts.values())
        )
        ids = {}
        progresses = {}
        while ray.get(ph.get_complete.remote()) != len(new_texts):
            try:
                id_ = ray.get(ph.get.remote())
            except Empty:
                continue
            if id_ not in ids:
                ids[id_] = progress.add_task(str(id_), total=len(new_texts[id_]))
                progresses[id_] = 0
            progress.advance(ids[id_], 1)
            progress.advance(main_id, 1)
            progresses[id_] += 1
            if len(new_texts[id_]) <= progresses[id_]:
                progress.update(ids[id_], visible=False)
                progress.remove_task(ids[id_])
                del progresses[id_]
                del ids[id_]
    preresult = ray.get(futures)

    result = {}
    for i in preresult:
        if i is None:
            continue
        k, v = list(i.items())[0]
        result[k] = v

    for file in track(
        glob.glob(
            str(Path(__file__).parent / f"tmp/{glob.escape(export_id)}_*.tmp.png")
        ),
        description="Cleaning up",
        transient=True,
    ):
        os.remove(file)
    for file in track(
        glob.glob(str(Path(__file__).parent / f"tmp/{glob.escape(export_id)}.2.pkl")),
        description="Cleaning up",
    ):
        os.remove(file)
    log.info("Render complete")

    return result


def render(
    components: Pla2File,
    zoom: ZoomParams,
    skin: Skin = Skin.from_name("default"),
    export_id: str = "unnamed",
    save_images: bool = True,
    save_dir: Path = Path.cwd(),
    assets_dir: Path = Path(__file__).parent / "skins" / "assets",
    processes: int = psutil.cpu_count(),
    tiles: list[TileCoord] | None = None,
    offset: tuple[RealNum, RealNum] = (0, 0),
    batch_size: int = 8,
) -> dict[TileCoord, Image.Image]:
    # noinspection GrazieInspection
    """
    Renders tiles from given coordinates and zoom values.

    .. warning::
        Run this function under ``if __name__ == "__main__"`` if ``use_ray`` is False, or else there would be a lot of
        multiprocessing RuntimeErrors.

    :param Pla2File components: a JSON of components
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
    :param int batch_size: The batch size for part 1 of the rendering

    :returns: Given in the form of ``{tile_coord: image}``
    :rtype: dict[TileCoord, Image.Image]
    """
    prepare_render(components, zoom, export_id, skin, tiles, offset)

    log.info("Initialising Ray...")
    ray.init(num_cpus=processes)
    render_part1_ray(components, zoom, export_id, skin, assets_dir, batch_size)
    render_part2(export_id)
    return render_part3_ray(export_id, skin, save_images, save_dir)
