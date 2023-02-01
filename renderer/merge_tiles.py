from __future__ import annotations

import glob
import logging
import re
from pathlib import Path

from PIL import Image
from rich.progress import track

from ._internal import str_to_tuple
from ._internal.logger import log
from .types.coord import TileCoord


def merge_tiles(
    images: Path | dict[TileCoord, Image],
    save_images: bool = True,
    save_dir: Path = Path.cwd(),
    zoom: list[int] | None = None,
) -> dict[int, Image.Image]:
    """
    Merges tiles rendered by :py:func:`render`.

    :param images: Give in the form of ``(tile coord): (PIL Image)``, like the return value of :py:func:`render`,
        or as a path to a directory.
    :type images: Path | dict[TileCoord, Image]
    :param bool save_images: whether to save the tile images in a folder or not
    :param Path save_dir: the directory to save tiles in
    :param zoom: if left empty, automatically calculates all zoom values based on tiles;
        otherwise, the layers of zoom to merge.
    :type zoom: list[int] | None

    :returns: Given in the form of ``(Zoom): (PIL Image)``
    :rtype: dict[int, Image.Image]
    """
    if zoom is None:
        zoom = []
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    image_dict = {}
    tile_return = {}
    if isinstance(images, Path):
        for d in track(
            glob.glob(str(images / "*.png")), description="[green]Retrieving images..."
        ):
            regex = re.search(r"(-?\d+, -?\d+, -?\d+)\.png$", d)
            if regex is None:
                continue
            coord = TileCoord(*str_to_tuple(regex.group(1)))
            image_dict[coord] = Image.open(d)
    else:
        image_dict = images
    log.info("[green]Determining zoom levels...")
    if not zoom:
        zoom = list({c.z for c in image_dict.keys()})
    for z in zoom:
        log.info(f"Zoom {z}: [dim white]Determining tiles to be merged")
        to_merge = {k: v for k, v in image_dict.items() if k.z == z}

        tile_coords = list(to_merge.keys())
        x_max, x_min, y_max, y_min = TileCoord.bounds(tile_coords)
        tile_size = list(image_dict.values())[0].size[0]
        log.info(
            f"Zoom {z}: [dim white]Creating image {tile_size*(x_max-x_min+1)}x{tile_size*(y_max-y_min+1)}"
        )
        i = Image.new(
            "RGBA",
            (tile_size * (x_max - x_min + 1), tile_size * (y_max - y_min + 1)),
            (0, 0, 0, 0),
        )
        px = 0
        py = 0
        merged = 0
        for x in track(
            range(x_min, x_max + 1), description=f"Zoom {z}: [dim white]Pasting tiles"
        ):
            for y in range(y_min, y_max + 1):
                if TileCoord(z, x, y) in to_merge.keys():
                    i.paste(to_merge[TileCoord(z, x, y)], (px, py))
                    merged += 1
                py += tile_size
            px += tile_size
            py = 0
        # tile_return[tile_components] = im
        if save_images:
            log.info(f"Zoom {z}: [dim white]Saving image")
            i.save(save_dir / f"merge_{z}.png", "PNG")
        tile_return[z] = i

    log.info("[green]All merges complete")
    return tile_return
