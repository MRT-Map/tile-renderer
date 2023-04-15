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
from .multiprocess import ProgressHandler, multiprocess
from .utils import TextObject, part_dir, wip_tiles_dir


def render_part3(
    config: Config,
    save_dir: Path | None = None,
    serial: bool = False,
    batch_size: int = psutil.cpu_count(),
) -> dict[TileCoord, Image.Image]:
    """Part 3 of the rendering job. Check render() for the full list of parameters"""
    tile_coords = []
    for file in glob.glob(str(wip_tiles_dir(config) / f"*.png")):
        re_result = re.search(rf"(-?\d+), (-?\d+), (-?\d+)\.png$", file)
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

    pre_result = multiprocess(
        tile_coords,
        (config, save_dir),
        _draw_text,
        "[green]Rendering texts",
        len(tile_coords),
        batch_size,
        8,
        serial,
    )
    result = {a: b for a, b in pre_result}

    shutil.rmtree(config.temp_dir / config.export_id)
    log.info("Render complete")

    return result


def _draw_text(
    ph: ObjectRef[ProgressHandler] | None,  # type: ignore
    tile_coord: TileCoord,
    const_data: tuple[Config, Path],
) -> tuple[TileCoord, Image.Image] | None:
    config, save_dir = const_data
    logging.getLogger("PIL").setLevel(logging.CRITICAL)

    image = Image.open(wip_tiles_dir(config) / f"{tile_coord}.png").convert("RGBA")
    try:
        with open(part_dir(config, 2) / f"tile_{tile_coord}.dill", "rb") as f:
            text_list: list[TextObject] = dill.load(f)
    except FileNotFoundError:
        text_list = []

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

    if ph:
        ph.add.remote(tile_coord)
        ph.complete.remote(tile_coord)  # type: ignore

    return tile_coord, image
