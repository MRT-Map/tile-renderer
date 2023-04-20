from __future__ import annotations

from typing import TYPE_CHECKING

import dill
from rich.progress import track

from .multiprocess import MultiprocessConfig, ProgressHandler, multiprocess
from .part1 import _needs_con_rendering

if TYPE_CHECKING:
    from ray.types import ObjectRef
    from ..misc_types.zoom_params import ZoomParams
    from ..skin_type import Skin
    from ..misc_types.config import Config

from .._internal.logger import log
from ..misc_types.coord import TileCoord, Vector, WorldLine
from ..misc_types.pla2 import Component, Pla2File
from .utils import part_dir


def _remove_unknown_component_types(components: Pla2File, skin: Skin) -> list[str]:
    remove_list: list[str] = []
    for component in components.components:
        if component.type not in skin.order:
            remove_list.append(component.fid)
    for component_id in remove_list:
        del components[component_id]
    return remove_list


def _sort_by_tiles(
    tiles: list[TileCoord],
    components: Pla2File,
    zoom: ZoomParams,
) -> dict[TileCoord, list[Component]]:
    tile_list: dict[TileCoord, list[Component]] = {}
    for tile in tiles:
        tile_list[tile] = []
    for component in components:
        rendered_in = component.nodes.to_tiles(zoom)
        for tile in rendered_in:
            if tile in tile_list:
                tile_list[tile].append(component)
    return tile_list


def _process_tiles(
    tile_list: dict[TileCoord, list[Component]],
    skin: Skin,
) -> dict[TileCoord, list[list[Component]]]:
    grouped_tile_list: dict[TileCoord, list[list[Component]]] = {}
    for tile_coord, tile_components in track(
        tile_list.items(),
        description="Processing tiles",
    ):
        # sort components in tiles by layer
        sorted_tile_components: dict[float, list[Component]] = {}
        for component in tile_components:
            if component.layer not in sorted_tile_components.keys():
                sorted_tile_components[component.layer] = []
            sorted_tile_components[component.layer].append(component)

        # sort components in layers in files by type
        sorted_tile_components = {
            layer: sorted(component_list, key=lambda x: skin.order.index(x.type))
            for layer, component_list in sorted_tile_components.items()
        }

        # merge layers
        merged_tile_components = []
        layers = sorted(sorted_tile_components.keys())
        for layer in layers:
            for component in sorted_tile_components[layer]:
                merged_tile_components.append(component)

        # groups components of the same type if "road" tag present
        grouped_tile_components: list[list[Component]] = [[]]
        for i, component in enumerate(merged_tile_components):
            grouped_tile_components[-1].append(component)
            if i != len(merged_tile_components) - 1 and (
                merged_tile_components[i + 1].type != component.type
                or "road" not in skin[component.type].tags
            ):
                grouped_tile_components.append([])
        if grouped_tile_components != [[]]:
            grouped_tile_list[tile_coord] = grouped_tile_components

    return grouped_tile_list


def prepare_render(
    components: Pla2File,
    config: Config,
    tiles: list[TileCoord] | None = None,
    zooms: list[int] | None = None,
    offset: Vector = Vector(0, 0),  # noqa: B008
    prepare_mp_config: MultiprocessConfig = MultiprocessConfig(),  # noqa: B008
) -> dict[TileCoord, list[list[Component]]]:
    """The data-preparing step of the rendering job. Check render() for the full list of parameters"""
    log.info("Offsetting coordinates...")
    for component in components:
        component.nodes = WorldLine([coord + offset for coord in component.nodes])

    if tiles is None or len(tiles) == 0:
        log.info("Finding tiles...")
        tiles = Component.rendered_in(components.components, config.zoom)
    if zooms is not None and len(zooms) != 0:
        tiles = [tc for tc in tiles if tc.z in zooms]

    log.info("Removing components with unknown type...")
    remove_list = _remove_unknown_component_types(components, config.skin)
    if remove_list:
        log.warning("The following components were removed: " + " | ".join(remove_list))

    log.info("Sorting components by tiles...")
    tile_list = _sort_by_tiles(tiles, components, config.zoom)

    grouped_tile_list = _process_tiles(tile_list, config.skin)

    def dump_data(
        ph: ObjectRef[ProgressHandler[TileCoord]] | None,
        cgc: tuple[TileCoord, list[list[Component]]],
        config_: Config,
    ) -> None:
        coord, grouped_components = cgc
        with (part_dir(config_, 0) / f"tile_{coord}.dill").open("wb") as f:
            dill.dump(grouped_components, f)
        if ph:
            ph.add.remote(coord)

    multiprocess(
        list(grouped_tile_list.items()),
        config,
        dump_data,
        "Dumping data",
        len(grouped_tile_list),
        prepare_mp_config,
    )

    num_rendering_ops = _count_num_rendering_ops(grouped_tile_list, config)

    with (part_dir(config, 0) / "processed.dill").open("wb") as f2:
        dill.dump((components, num_rendering_ops), f2)

    return grouped_tile_list


def _count_num_rendering_ops(
    grouped_tile_list: dict[TileCoord, list[list[Component]]],
    config: Config,
) -> int:
    operations = 0

    tile_coord: TileCoord
    tile_components: list[list[Component]]
    for tile_coord, tile_components in track(
        grouped_tile_list.items(),
        description="Counting operations",
    ):
        if not tile_components:
            continue

        for group in tile_components:
            type_info = config.skin[group[0].type]
            style = type_info[config.zoom.max - tile_coord[0]]
            for step in style:
                operations += len(group)

                if _needs_con_rendering(type_info, step):
                    operations += 1

    return operations
