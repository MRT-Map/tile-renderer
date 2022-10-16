from __future__ import annotations

from pathlib import Path

import psutil
import ray
import vector
from PIL import Image
from vector import Vector2D

from renderer.internals.logger import log
from renderer.render.part1 import render_part1
from renderer.render.part2 import render_part2
from renderer.render.part3 import render_part3
from renderer.render.prepare import prepare_render
from renderer.types.coord import TileCoord
from renderer.types.pla2 import Pla2File
from renderer.types.skin import Skin
from renderer.types.zoom_params import ZoomParams


def render(
    components: Pla2File,
    zoom: ZoomParams,
    skin: Skin = Skin.from_name("default"),
    export_id: str = "unnamed",
    save_images: bool = True,
    save_dir: Path = Path.cwd() / "tiles",
    assets_dir: Path = Path(__file__).parent.parent / "skins" / "assets",
    temp_dir: Path = Path.cwd() / "temp",
    processes: int = psutil.cpu_count(),
    tiles: list[TileCoord] | None = None,
    offset: Vector2D = vector.obj(x=0, y=0),
    part1_batch_size: int = 8,
    part1_chunk_size: int = 8,
    part1_serial: bool = False,
) -> dict[TileCoord, Image.Image]:
    # noinspection GrazieInspection
    """
    Renders tiles from given coordinates and zoom values.

    .. warning::
        Run this function under ``if __name__ == "__main__"`` if ``use_ray`` is False, or else there would be a lot of
        multiprocessing RuntimeErrors.

    :param Pla2File components: a JSON of components
    :param ZoomParams zoom: a ZoomParams object
    :param Skin skin: The skin to use for rendering the tiles
    :param str export_id: The name of the rendering task
    :param int save_images: whether to save the tile images in a folder or not
    :param Path save_dir: the directory to save tiles in
    :param Path assets_dir: the asset directory for the skin
    :param Path temp_dir: TODO
    :param int processes: The amount of processes to run for rendering
    :param tiles: a list of tiles to render
    :type tiles: list[TileCoord] | None
    :param offset: the offset to shift all node coordinates by, given as ``(x,y)``
    :type offset: tuple[float, float]
    :param int part1_batch_size: The batch size for part 1 of the rendering
    :param int part1_chunk_size: The chunk size for part 1 of the rendering
    :param int part1_serial: TODO

    :returns: Given in the form of ``{tile_coord: image}``
    :rtype: dict[TileCoord, Image.Image]
    """

    log.debug("Creating save & temp directories")
    save_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    prepare_render(components, zoom, export_id, skin, tiles, offset, temp_dir)

    if not part1_serial:
        log.info(f"Initialising Ray with {processes=}...")
        ray.init(num_cpus=processes)

    render_part1(
        zoom,
        export_id,
        skin,
        assets_dir,
        part1_batch_size,
        part1_chunk_size,
        temp_dir,
        part1_serial,
    )
    render_part2(export_id, temp_dir)
    return render_part3(export_id, skin, save_images, save_dir, temp_dir)
