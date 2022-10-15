from __future__ import annotations

import gc
import glob
import logging
import os
import pickle
import re
import traceback
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from queue import Empty

import ray
from PIL import Image, ImageDraw
from ray import ObjectRef
from rich.progress import Progress, track
from rich.traceback import install

from renderer.internals.logger import log
from renderer.render.utils import ProgressHandler
from renderer.types.coord import TileCoord, WorldCoord
from renderer.types.pla2 import Component, Pla2File
from renderer.types.skin import Skin, _TextObject
from renderer.types.zoom_params import ZoomParams


@dataclass(frozen=True, init=True)
class Part1Consts:
    coord_to_comp: dict[WorldCoord, list[Component]]
    skin: Skin
    zoom: ZoomParams
    assets_dir: Path
    export_id: str
    temp_dir: Path


def _pre_draw_components(
    ph: ProgressHandler | None, tile_coords: list[TileCoord], consts: Part1Consts
) -> dict[TileCoord, list[_TextObject]]:
    # noinspection PyBroadException
    try:
        install(show_locals=True)
        logging.getLogger("fontTools").setLevel(logging.CRITICAL)
        logging.getLogger("PIL").setLevel(logging.CRITICAL)
        results = {}
        for tile_coord in tile_coords:
            path = consts.temp_dir / f"{consts.export_id}_{tile_coord}.0.pkl"
            with open(path, "rb") as f:
                tile_components = pickle.load(f)

            out = _draw_components(ph, tile_coord, tile_components, consts)

            os.remove(path)
            if out is not None:
                with open(
                    consts.temp_dir / f"{consts.export_id}_{tile_coord}.1.pkl", "wb"
                ) as f:
                    pickle.dump({out[0]: out[1]}, f)
            results[out[0]] = out[1]
        if ph:
            ph.request_new_task.remote()
        return results
    except Exception as e:
        log.error(f"Error in ray task: {e!r}")
        log.error(traceback.format_exc())
        ph.request_new_task.remote()


def render_part1(
    zoom: ZoomParams,
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    assets_dir: Path = Path(__file__).parent.parent / "skins" / "assets",
    batch_size: int = 8,
    temp_dir: Path = Path.cwd() / "temp",
    serial: bool = False,
) -> dict[TileCoord, list[_TextObject]]:
    tile_coords = []
    with open(temp_dir / f"{export_id}.processed.0.pkl", "rb") as f:
        components = pickle.load(f)

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

    coord_to_comp: dict[WorldCoord, list[Component]] = {}
    for comp in track(components.components, "Generating coord_to_comp"):
        for node in comp.nodes:
            coord_to_comp.setdefault(node, []).append(comp)

    consts: ObjectRef[Part1Consts] = ray.put(
        Part1Consts(
            coord_to_comp,
            skin,
            zoom,
            assets_dir,
            export_id,
            temp_dir,
        )
    )

    log.info(
        f"Rendering components in {len(tile_coords)} tiles ({sum(operations.values())} operations)..."
    )

    if serial:
        out = {}
        for tile_coord in track(tile_coords, "Rendering components"):
            (tc, lto) = _pre_draw_components(None, [tile_coord], ray.get(consts))
            out[tc] = lto
        return out

    n = 5  # TODO param for this
    tile_chunks = [tile_coords[i : i + n] for i in range(0, len(tile_coords), n)]
    ph = ProgressHandler.remote()

    futures = [
        ray.remote(_pre_draw_components).remote(ph, tile_coords, consts)
        for tile_coords in track(tile_chunks[:batch_size], "Spawning initial tasks")
    ]
    cursor = batch_size
    with Progress() as progress:
        main_id = progress.add_task(
            "Rendering components", total=sum(operations.values())
        )
        ids = {}
        progresses = {}
        while ray.get(ph.get_complete.remote()) != len(tile_coords):
            while ph.needs_new_task.remote() and cursor < len(tile_chunks):
                futures.append(
                    ray.remote(_pre_draw_components).remote(
                        ph, tile_chunks[cursor], consts
                    )
                )
                cursor += 1
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
    preresult: list[dict[TileCoord, list[_TextObject]]] = ray.get(futures)
    result = {}
    for a in preresult:
        result.update(a)
    return result


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
    ph: ProgressHandler | None,
    tile_coord: TileCoord,
    tile_components: list[list[Component]],
    consts: Part1Consts,
) -> tuple[TileCoord, list[_TextObject]]:
    size = consts.zoom.range * 2 ** (consts.zoom.max - tile_coord[0])
    img = Image.new(
        mode="RGBA", size=(consts.skin.tile_size,) * 2, color=consts.skin.background
    )
    imd = ImageDraw.Draw(img)
    text_list: list[_TextObject] = []
    points_text_list: list[_TextObject] = []

    for group in tile_components:
        type_info = consts.skin[group[0].type]
        style = type_info[consts.zoom.max - tile_coord[0]]
        for step in style:
            for component in group:
                coords = component.nodes.to_image_line(consts.skin, tile_coord, size)

                args = {
                    "point": {
                        "circle": (imd, coords),
                        "text": (
                            imd,
                            coords,
                            component.display_name,
                            consts.assets_dir,
                            points_text_list,
                            tile_coord,
                            consts.skin.tile_size,
                        ),
                        "square": (imd, coords),
                        "image": (img, coords, consts.assets_dir),
                    },
                    "line": {
                        "text": (
                            imd,
                            img,
                            coords,
                            consts.assets_dir,
                            component,
                            text_list,
                            tile_coord,
                            consts.skin.tile_size,
                        ),
                        "back": (imd, coords),
                        "fore": (imd, coords),
                    },
                    "area": {
                        "bordertext": (
                            imd,
                            coords,
                            component,
                            consts.assets_dir,
                            text_list,
                            tile_coord,
                            consts.skin.tile_size,
                        ),
                        "centertext": (
                            imd,
                            coords,
                            component,
                            consts.assets_dir,
                            text_list,
                            tile_coord,
                            consts.skin.tile_size,
                        ),
                        "fill": (imd, img, coords, component, tile_coord, size),
                        "centerimage": (img, coords, consts.assets_dir),
                    },
                }

                if step.layer not in args[type_info.shape].keys():
                    raise KeyError(f"{step.layer} is not a valid layer")
                # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}")
                step.render(*args[type_info.shape][step.layer])

                if ph:
                    ph.add.remote(tile_coord)

            if (
                type_info.shape == "line"
                and "road" in type_info.tags
                and step.layer == "back"
            ):
                for coord in chain(*(c.nodes.coords for c in group)):
                    coord: WorldCoord
                    inter = Image.new("RGBA", (consts.skin.tile_size,) * 2, (0,) * 4)
                    for con_component in consts.coord_to_comp[coord]:
                        if "road" not in consts.skin[con_component.type].tags:
                            continue
                        con_info = consts.skin[con_component.type]
                        for con_step in con_info[consts.zoom.max - tile_coord.z]:
                            if con_step.layer != "fore":
                                continue

                            con_coords = con_component.nodes.to_image_line(
                                consts.skin, tile_coord, size
                            )

                            con_img = Image.new(
                                "RGBA", (consts.skin.tile_size,) * 2, (0,) * 4
                            )
                            con_imd = ImageDraw.Draw(con_img)
                            con_step: Skin.ComponentTypeInfo.LineFore
                            con_step.render(con_imd, con_coords)

                            con_mask_img = Image.new(
                                "RGBA", (consts.skin.tile_size,) * 2, (0,) * 4
                            )
                            con_mask_imd = ImageDraw.Draw(con_mask_img)
                            con_mask_imd.ellipse(
                                (
                                    coord.x
                                    - (max(con_step.width, step.width) * 2) / 2
                                    + 1,
                                    coord.y
                                    - (max(con_step.width, step.width) * 2) / 2
                                    + 1,
                                    coord.x + (max(con_step.width, step.width) * 2) / 2,
                                    coord.y + (max(con_step.width, step.width) * 2) / 2,
                                ),
                                fill="#000000",
                            )

                            inter.paste(con_img, (0, 0), con_mask_img)
                    img.paste(inter, (0, 0), inter)

                if ph:
                    ph.add.remote(tile_coord)

    text_list += points_text_list
    text_list.reverse()

    img.save(consts.temp_dir / f"{consts.export_id}_{tile_coord}.tmp.webp", "webp")
    if ph:
        ph.complete.remote()

    return tile_coord, text_list
