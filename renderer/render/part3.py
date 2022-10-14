from __future__ import annotations

import glob
import logging
import os
import pickle
from pathlib import Path
from queue import Empty

from PIL import Image
from rich.progress import Progress, track

from renderer.internals.logger import log
from renderer.render.utils import ProgressHandler
from renderer.types.coord import TileCoord
from renderer.types.skin import Skin, _TextObject


def render_part3_ray(
    export_id: str,
    skin: Skin = Skin.from_name("default"),
    save_images: bool = True,
    save_dir: Path = Path.cwd(),
    temp_dir: Path = Path.cwd() / "temp",
) -> dict[TileCoord, Image.Image]:
    import ray

    with open(temp_dir / f"{export_id}.2.pkl", "rb") as f:
        new_texts, total_texts = pickle.load(f)
    new_texts: dict[TileCoord, list[_TextObject]]
    total_texts: int

    log.info(f"Rendering images in {len(new_texts)} tiles...")
    ph = ProgressHandler.remote()
    futures = [
        ray.remote(_draw_text).remote(
            ph, tile_coord, text_list, save_images, save_dir, skin, export_id
        )
        for tile_coord, text_list in track(
            new_texts.items(), description="Dispatching tasks"
        )
    ]
    with Progress() as progress:
        main_id = progress.add_task(
            "Rendering texts", total=sum(len(ls) for ls in new_texts.values())
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


def _draw_text(
    ph,
    tile_coord: TileCoord,
    text_list: list[_TextObject],
    save_images: bool,
    save_dir: Path,
    skin: Skin,
    export_id: str,
) -> dict[TileCoord, Image.Image]:
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    image = Image.open(
        Path(__file__).parent.parent / f"tmp/{export_id}_{tile_coord}.tmp.png"
    )
    # print(text_list)
    for text in text_list:
        # logger.log(f"Text {processed}/{len(text_list)} pasted")
        for img, center in zip(text.image, text.center):
            image.paste(
                img,
                (
                    int(center.x - tile_coord.x * skin.tile_size - img.width / 2),
                    int(center.y - tile_coord.y * skin.tile_size - img.height / 2),
                ),
                img,
            )
        ph.add.remote(tile_coord)

    # tileReturn[tile_coord] = im
    if save_images:
        image.save(save_dir / f"{tile_coord}.png", "PNG")
    ph.complete.remote()

    return {tile_coord: image}
