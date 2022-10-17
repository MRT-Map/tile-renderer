from __future__ import annotations

import gc
import glob
import logging
import os
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
    chunks: list[dict[TileCoord, list[_TextObject]]],
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
    new_texts: dict[TileCoord, list[_TextObject]] = {}
    total_texts = 0
    for file in glob.glob(str(part_dir(temp_dir, export_id, 2) / "*.dill")):
        with open(file, "rb") as f:
            z_new_texts, z_total_texts = dill.load(f)
            new_texts.update(z_new_texts)
            total_texts += z_total_texts

    log.info(f"Rendering texts in {len(new_texts)} tiles...")
    if serial:
        preresult = [
            _draw_text(None, {tc: tl}, save_images, save_dir, skin, export_id, temp_dir)
            for tc, tl in track(new_texts.items(), description="[green]Rendering texts")
        ]
    else:
        batch_size = 8
        chunks = [
            {k: v for k, v in list(new_texts.items())[i : i + 10]}
            for i in range(0, len(new_texts), 10)
        ]
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
            main_id = progress.add_task("[green]Rendering texts", total=len(new_texts))
            num_complete = 0
            while num_complete < len(new_texts):
                id_: TileCoord | None = ray.get(ph.get.remote())
                if id_ is None:
                    continue
                progress.advance(main_id, 1)
                num_complete += 1
            progress.update(main_id, completed=len(new_texts))

        preresult = ray.get(ray.get(future_refs))
    result = {}
    for i in preresult:
        result.update(i)

    shutil.rmtree(temp_dir / export_id)
    log.info("Render complete")

    return result


def _draw_text(
    ph: ObjectRef[ProgressHandler] | None,
    text_lists: dict[TileCoord, list[_TextObject]],
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
        for tile_coord, text_list in text_lists.items():
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

        return out
    except Exception as e:
        log.error(f"Error in ray task: {e!r}")
        log.error(traceback.format_exc())
