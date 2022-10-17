from __future__ import annotations

import gc
import glob
import logging
import os
import re
import shutil
import traceback
from pathlib import Path

import dill
import ray
from PIL import Image
from ray import ObjectRef
from rich.progress import Progress, track

from renderer.internals.logger import log
from renderer.render.utils import ProgressHandler, _TextObject, part_dir, wip_tiles_dir
from renderer.types.coord import TileCoord
from renderer.types.skin import Skin


@ray.remote
def task_spawner(
    ph: ObjectRef[ProgressHandler] | None,
    chunks: list[list[TileCoord]],
    save_images: bool,
    save_dir: Path,
    skin: Skin,
    export_id: str,
    temp_dir: Path,
    cursor: int,
    futures: list[ObjectRef[dict[TileCoord, Image.Image]]],
) -> list[ObjectRef[dict[TileCoord, Image.Image]]]:
    while cursor < len(chunks):
        if ray.get(ph.needs_new_task.remote()):
            futures.append(
                ray.remote(_draw_text).remote(
                    ph,
                    chunks[cursor],
                    save_images,
                    save_dir,
                    skin,
                    export_id,
                    temp_dir,
                )
            )
            cursor += 1
    return futures


def render_part3(
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    save_images: bool = True,
    save_dir: Path = Path.cwd(),
    temp_dir: Path = Path.cwd() / "temp",
    serial: bool = False,
) -> dict[TileCoord, Image.Image]:
    tile_coords = []
    for file in glob.glob(str(part_dir(temp_dir, export_id, 2) / f"tile_*.dill")):
        re_result = re.search(rf"tile_(-?\d+), (-?\d+), (-?\d+)\.dill$", file)
        tile_coords.append(
            TileCoord(
                int(re_result.group(1)),
                int(re_result.group(2)),
                int(re_result.group(3)),
            )
        )

    log.info(f"Rendering texts in {len(tile_coords)} tiles...")
    if serial:
        preresult = [
            _draw_text(
                None, [tile_coord], save_images, save_dir, skin, export_id, temp_dir
            )
            for tile_coord in track(tile_coords, description="[green]Rendering texts")
        ]
    else:
        batch_size = 8
        chunks = [tile_coords[i : i + 10] for i in range(0, len(tile_coords), 10)]
        gc.collect()

        ph = ProgressHandler.remote()
        futures = [
            ray.remote(_draw_text).remote(
                ph,
                text_lists,
                save_images,
                save_dir,
                skin,
                export_id,
                temp_dir,
            )
            for text_lists in track(chunks[:batch_size], "Spawning initial tasks")
        ]
        future_refs = task_spawner.remote(
            ph,
            chunks,
            save_images,
            save_dir,
            skin,
            export_id,
            temp_dir,
            batch_size,
            futures,
        )
        with Progress() as progress:
            main_id = progress.add_task(
                "[green]Rendering texts", total=len(tile_coords)
            )
            num_complete = 0
            while num_complete < len(chunks):
                id_: TileCoord | None = ray.get(ph.get.remote())
                if id_ is None:
                    continue
                progress.advance(main_id, 1)
                num_complete += 1
            progress.update(main_id, completed=len(tile_coords))

        preresult = ray.get(ray.get(future_refs))
    result = {}
    for i in preresult:
        result.update(i)

    shutil.rmtree(temp_dir / export_id)
    log.info("Render complete")

    return result


def _draw_text(
    ph: ObjectRef[ProgressHandler] | None,
    tile_coords: list[TileCoord],
    save_images: bool,
    save_dir: Path,
    skin: Skin,
    export_id: str,
    temp_dir: Path,
) -> dict[TileCoord, Image.Image]:
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    # noinspection PyBroadException
    try:
        out = {}
        for tile_coord in tile_coords:
            with open(
                part_dir(temp_dir, export_id, 2) / f"tile_{tile_coord}.dill", "rb"
            ) as f:
                text_list: list[_TextObject] = dill.load(f)
            try:
                image = Image.open(
                    wip_tiles_dir(temp_dir, export_id) / f"{tile_coord}.png"
                )
            except FileNotFoundError:
                if ph:
                    ph.add.remote(tile_coord)
                continue
            for text in text_list:
                for img, center in zip(text.image, text.center):
                    img = _TextObject.uuid_to_img(img, temp_dir, export_id)
                    image.paste(
                        img,
                        (
                            int(
                                center.x - tile_coord.x * skin.tile_size - img.width / 2
                            ),
                            int(
                                center.y
                                - tile_coord.y * skin.tile_size
                                - img.height / 2
                            ),
                        ),
                        img,
                    )

            # antialiasing
            image = image.resize(
                (image.width * 4, image.height * 4), resample=Image.BOX
            ).resize(image.size, resample=Image.ANTIALIAS)

            if save_images:
                image.save(save_dir / f"{tile_coord}.webp", "webp", quality=95)
            os.remove(wip_tiles_dir(temp_dir, export_id) / f"{tile_coord}.png")
            out[tile_coord] = image

            if ph:
                ph.add.remote(tile_coord)
        if ph:
            ph.request_new_task.remote()

        return out
    except Exception as e:
        log.error(f"Error in ray task: {e!r}")
        log.error(traceback.format_exc())
