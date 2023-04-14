from __future__ import annotations

import gc
import glob
import logging
import os
import re
import shutil
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

import dill
import psutil
import ray
from PIL import Image
from ray import ObjectRef
from rich.progress import Progress, track

if TYPE_CHECKING:
    from .. import Config
from .._internal.logger import log
from ..misc_types.coord import TileCoord
from .utils import ProgressHandler, TextObject, part_dir, wip_tiles_dir


@ray.remote
def task_spawner(
    ph: ObjectRef[ProgressHandler],  # type: ignore
    config: Config,
    chunks: list[list[TileCoord]],
    save_dir: Path | None,
    cursor: int,
    futures: list[ObjectRef[dict[TileCoord, Image.Image] | None]],  # type: ignore
) -> list[ObjectRef[dict[TileCoord, Image.Image] | None]]:  # type: ignore
    """The task spawner used for part 3"""
    while cursor < len(chunks):
        if ray.get(ph.needs_new_task.remote()):  # type: ignore
            output = ray.remote(_draw_text).remote(  # type: ignore
                ph,
                config,
                chunks[cursor],
                save_dir,
            )
            futures.append(output)
            cursor += 1
    return futures


def render_part3(
    config: Config,
    save_dir: Path | None = None,
    serial: bool = False,
    batch_size: int = psutil.cpu_count(),
) -> dict[TileCoord, Image.Image]:
    """Part 3 of the rendering job. Check render() for the full list of parameters"""
    tile_coords = []
    for file in glob.glob(str(part_dir(config, 2) / f"tile_*.dill")):
        re_result = re.search(rf"tile_(-?\d+), (-?\d+), (-?\d+)\.dill$", file)
        if re_result is None:
            raise ValueError("Dill object was not saved properly")
        tile_coords.append(
            TileCoord(
                int(re_result.group(1)),
                int(re_result.group(2)),
                int(re_result.group(3)),
            )
        )

    log.info(f"Rendering texts in {len(tile_coords)} tiles...")
    if serial:
        pre_result: list[dict[TileCoord, Image.Image] | None] = [
            _draw_text(
                None,
                config,
                [tile_coord],
                save_dir,
            )
            for tile_coord in track(tile_coords, description="[green]Rendering texts")
        ]
    else:
        chunks = [tile_coords[i : i + 10] for i in range(0, len(tile_coords), 10)]
        gc.collect()

        ph = ProgressHandler.remote()  # type: ignore
        futures = [
            ray.remote(_draw_text).remote(  # type: ignore
                ph,
                config,
                text_lists,
                save_dir,
            )
            for text_lists in track(chunks[:batch_size], "Spawning initial tasks")
        ]
        future_refs: ObjectRef[list[ObjectRef[dict[TileCoord, Image.Image] | None]]]  # type: ignore
        future_refs = task_spawner.remote(
            ph,
            config,
            chunks,
            save_dir,
            batch_size,
            futures,
        )
        with Progress() as progress:
            main_id = progress.add_task("[green]Rendering texts", total=len(chunks))
            num_complete = 0
            while num_complete < len(chunks):
                id_: TileCoord | None = ray.get(ph.get.remote())
                if id_ is None:
                    continue
                progress.advance(main_id, 1)
                num_complete += 1
            progress.update(main_id, completed=len(tile_coords))

        pre_pre_result: list[ObjectRef[dict[TileCoord, Image.Image] | None]]  # type: ignore
        pre_pre_result = ray.get(future_refs)
        pre_result = ray.get(pre_pre_result)
    result: dict[TileCoord, Image.Image] = {}
    for i in pre_result:
        if i is not None:
            result.update(i)

    shutil.rmtree(config.temp_dir / config.export_id)
    log.info("Render complete")

    return result


def _draw_text(
    ph: ObjectRef[ProgressHandler] | None,  # type: ignore
    config: Config,
    tile_coords: list[TileCoord],
    save_dir: Path | None = None,
) -> dict[TileCoord, Image.Image] | None:
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    # noinspection PyBroadException
    try:
        out = {}
        for tile_coord in tile_coords:
            with open(part_dir(config, 2) / f"tile_{tile_coord}.dill", "rb") as f:
                text_list: list[TextObject] = dill.load(f)
            try:
                image = Image.open(wip_tiles_dir(config) / f"{tile_coord}.png").convert(
                    "RGBA"
                )
            except FileNotFoundError:
                if ph:
                    ph.add.remote(tile_coord)  # type: ignore
                continue

            # antialiasing
            image = image.resize(
                (image.width * 16, image.height * 16), resample=Image.BOX
            ).resize(image.size, resample=Image.ANTIALIAS)

            for text in text_list:
                for img_uuid, center in zip(text.image, text.center):
                    img = TextObject.uuid_to_img(img_uuid, config).convert("RGBA")
                    new_center = center.to_image_coord(tile_coord, config)
                    image.alpha_composite(
                        img,
                        (
                            int(new_center.x - img.width / 2),
                            int(new_center.y - img.height / 2),
                        ),
                    )

            if save_dir is not None:
                image.save(save_dir / f"{tile_coord}.webp", "webp", quality=95)
            os.remove(wip_tiles_dir(config) / f"{tile_coord}.png")
            out[tile_coord] = image

            if ph:
                ph.add.remote(tile_coord)  # type: ignore
        if ph:
            ph.request_new_task.remote()  # type: ignore

        return out
    except Exception as e:
        log.error(f"Error in ray task: {e!r}")
        log.error(traceback.format_exc())
        return None
