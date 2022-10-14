from __future__ import annotations

import gc
import glob
import logging
import os
import pickle
import re
from itertools import chain
from pathlib import Path
from queue import Empty

import ray
from PIL import Image, ImageDraw
from rich.progress import Progress, track

from renderer.internals.logger import log
from renderer.render.utils import ProgressHandler
from renderer.types.coord import TileCoord, WorldCoord
from renderer.types.pla2 import Component, Pla2File
from renderer.types.skin import Skin, _TextObject
from renderer.types.zoom_params import ZoomParams


def _pre_draw_components(
    ph: ProgressHandler,
    tile_coord: TileCoord,
    all_components: Pla2File,
    skin: Skin,
    zoom: ZoomParams,
    assets_dir: Path,
    export_id: str,
    temp_dir: Path,
) -> tuple[TileCoord, list[_TextObject]]:
    path = temp_dir / f"{export_id}_{tile_coord}.0.pkl"
    with open(path, "rb") as f:
        tile_components = pickle.load(f)
    logging.getLogger("fontTools").setLevel(logging.CRITICAL)
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    result = _draw_components(
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
        with open(temp_dir / f"{export_id}_{tile_coord}.1.pkl", "wb") as f:
            pickle.dump({result[0]: result[1]}, f)
    return result


def render_part1_ray(
    components: Pla2File,
    zoom: ZoomParams,
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    assets_dir: Path = Path(__file__).parent / "skins" / "assets",
    batch_size: int = 8,
    temp_dir: Path = Path.cwd() / "temp",
) -> dict[TileCoord, list[_TextObject]]:
    tile_coords = []
    for file in glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.0.pkl")):
        re_result = re.search(rf"_(-?\d+), (-?\d+), (-?\d+)\.0\.pkl$", file)
        tile_coords.append(
            TileCoord(
                int(re_result.group(1)),
                int(re_result.group(2)),
                int(re_result.group(3)),
            )
        )

    operations = _count_num_rendering_oprs(export_id, skin, zoom, temp_dir)
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


def _count_num_rendering_oprs(
    export_id: str, skin: Skin, zoom: ZoomParams, temp_dir: Path
) -> dict[TileCoord, int]:
    grouped_tile_list: dict[TileCoord, list[Pla2File]] = {}
    for file in track(
        glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.0.pkl")),
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


def _draw_components(
    ph,
    tile_coord: TileCoord,
    tile_components: list[list[Component]],
    all_components: Pla2File,
    skin: Skin,
    zoom: ZoomParams,
    assets_dir: Path,
    export_id: str,
) -> tuple[TileCoord, list[_TextObject]]:
    size = zoom.range * 2 ** (zoom.max - tile_coord[0])
    img = Image.new(mode="RGBA", size=(skin.tile_size,) * 2, color=skin.background)
    imd = ImageDraw.Draw(img)
    text_list: list[_TextObject] = []
    points_text_list: list[_TextObject] = []

    for group in tile_components:
        type_info = skin[group[0].type]
        style = type_info[zoom.max - tile_coord[0]]
        for step in style:
            for component in group:
                coords = component.nodes.to_image_line(skin, tile_coord, size)

                args = {
                    "point": {
                        "circle": (imd, coords),
                        "text": (
                            imd,
                            coords,
                            component.display_name,
                            assets_dir,
                            points_text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "square": (imd, coords),
                        "image": (img, coords, assets_dir),
                    },
                    "line": {
                        "text": (
                            imd,
                            img,
                            coords,
                            assets_dir,
                            component,
                            text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "back": (imd, coords),
                        "fore": (imd, coords),
                    },
                    "area": {
                        "bordertext": (
                            imd,
                            coords,
                            component,
                            assets_dir,
                            text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "centertext": (
                            imd,
                            coords,
                            component,
                            assets_dir,
                            text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "fill": (imd, img, coords, component, tile_coord, size),
                        "centerimage": (img, coords, assets_dir),
                    },
                }

                if step.layer not in args[type_info.shape].keys():
                    raise KeyError(f"{step.layer} is not a valid layer")
                # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}")
                step.render(*args[type_info.shape][step.layer])

                ph.add.remote(tile_coord)

            if (
                type_info.shape == "line"
                and "road" in type_info.tags
                and step.layer == "back"
            ):
                # logger.log("Rendering studs")
                attached: list[tuple[Component, WorldCoord]] = list(
                    chain(
                        *(
                            comp.find_components_attached(all_components)
                            for comp in group
                        )
                    )
                )
                for con_component, coord in attached:
                    if "road" not in skin[con_component.type].tags:
                        continue
                    con_info = skin[con_component.type]
                    for con_step in con_info[zoom.max - tile_coord.z]:
                        if con_step.layer in ["back", "text"]:
                            continue

                        con_coords = con_component.nodes.to_image_line(
                            skin, tile_coord, size
                        )

                        con_img = Image.new("RGBA", (skin.tile_size,) * 2, (0,) * 4)
                        con_imd = ImageDraw.Draw(con_img)
                        con_step: Skin.ComponentTypeInfo.LineFore
                        con_step.render(con_imd, con_coords)

                        con_mask_img = Image.new(
                            "RGBA", (skin.tile_size,) * 2, (0,) * 4
                        )
                        con_mask_imd = ImageDraw.Draw(con_mask_img)
                        con_mask_imd.ellipse(
                            (
                                coord.x - (max(con_step.width, step.width) * 2) / 2 + 1,
                                coord.y - (max(con_step.width, step.width) * 2) / 2 + 1,
                                coord.x + (max(con_step.width, step.width) * 2) / 2,
                                coord.y + (max(con_step.width, step.width) * 2) / 2,
                            ),
                            fill="#000000",
                        )

                        inter = Image.new("RGBA", (skin.tile_size,) * 2, (0,) * 4)
                        inter.paste(con_img, (0, 0), con_mask_img)
                        img.paste(inter, (0, 0), inter)

                ph.add.remote(tile_coord)

    text_list += points_text_list
    text_list.reverse()

    img.save(
        Path(__file__).parent.parent / f"tmp/{export_id}_{tile_coord}.tmp.png", "PNG"
    )
    ph.complete.remote()

    return tile_coord, text_list
