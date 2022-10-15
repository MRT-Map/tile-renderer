from __future__ import annotations

import pickle
from pathlib import Path

import vector
from rich.progress import track
from vector import Vector2D

from renderer.internals.logger import log
from renderer.types.coord import TileCoord, WorldCoord, WorldLine
from renderer.types.pla2 import Component, Pla2File
from renderer.types.skin import Skin
from renderer.types.zoom_params import ZoomParams


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
    temp_dir: Path = Path.cwd() / "temp",
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
        log.warning("The following components were removed: " + " | ".join(remove_list))

    log.info("Sorting components by tiles...")
    tile_list = _sort_by_tiles(tiles, components, zoom)

    grouped_tile_list = _process_tiles(tile_list, skin)

    for coord, grouped_components in track(
        grouped_tile_list.items(), description="Dumping data"
    ):
        with open(temp_dir / f"{export_id}_{coord}.0.pkl", "wb") as f:
            pickle.dump(grouped_components, f)
    with open(temp_dir / f"{export_id}.processed.0.pkl", "wb") as f:
        pickle.dump(components, f)

    return grouped_tile_list
