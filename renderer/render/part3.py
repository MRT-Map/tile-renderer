from __future__ import annotations

import glob
import logging
import os
import traceback
from pathlib import Path

import dill
from PIL import Image
from rich.progress import track

from renderer.internals.logger import log
from renderer.render.utils import _TextObject
from renderer.types.coord import TileCoord
from renderer.types.skin import Skin


def render_part3(
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    save_images: bool = True,
    save_dir: Path = Path.cwd(),
    temp_dir: Path = Path.cwd() / "temp",
) -> dict[TileCoord, Image.Image]:
    new_texts = {}
    total_texts = 0
    for file in glob.glob(str(temp_dir / f"{export_id}_*.2.dill")):
        with open(file, "rb") as f:
            z_new_texts, z_total_texts = dill.load(f)
            new_texts.update(z_new_texts)
            total_texts += z_total_texts

    log.info(f"Rendering texts in {len(new_texts)} tiles...")
    preresult = [
        _draw_text(
            tile_coord, text_list, save_images, save_dir, skin, export_id, temp_dir
        )
        for tile_coord, text_list in track(
            new_texts.items(), description="[green]Rendering texts"
        )
    ]

    result = {}
    for i in preresult:
        if i is None:
            continue
        k, v = list(i.items())[0]
        result[k] = v

    for file in track(
        glob.glob(str(temp_dir / f"tmp/{glob.escape(export_id)}_*.tmp.png")),
        description="Cleaning up",
        transient=True,
    ):
        os.remove(file)
    for file in track(
        glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.2.dill")),
        description="Cleaning up",
    ):
        os.remove(file)
    log.info("Render complete")

    return result


def _draw_text(
    tile_coord: TileCoord,
    text_list: list[_TextObject],
    save_images: bool,
    save_dir: Path,
    skin: Skin,
    export_id: str,
    temp_dir: Path,
) -> dict[TileCoord, Image.Image]:
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    # noinspection PyBroadException
    try:
        image = Image.open(temp_dir / f"{export_id}_{tile_coord}.tmp.png")
        for text in text_list:
            for img, center in zip(text.image, text.center):
                img = _TextObject.uuid_to_img(img, temp_dir)
                image.paste(
                    img,
                    (
                        int(center.x - tile_coord.x * skin.tile_size - img.width / 2),
                        int(center.y - tile_coord.y * skin.tile_size - img.height / 2),
                    ),
                    img,
                )

        # antialiasing
        image = image.resize(
            (image.width * 4, image.height * 4), resample=Image.BOX
        ).resize(image.size, resample=Image.ANTIALIAS)

        if save_images:
            image.save(save_dir / f"{tile_coord}.webp", "webp", quality=95)
        os.remove((temp_dir / f"{export_id}_{tile_coord}.tmp.png"))

        return {tile_coord: image}
    except Exception as e:
        log.error(f"Error in ray task: {e!r}")
        log.error(traceback.format_exc())
