from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import psutil
import ray
from PIL import Image

from .._internal.logger import log

if TYPE_CHECKING:
    from ..misc_types.config import Config
    from ..misc_types.pla2 import Pla2File

from ..misc_types.coord import TileCoord, Vector
from .part1 import render_part1
from .part2 import render_part2
from .part3 import render_part3
from .prepare import prepare_render


def render(
    components: Pla2File,
    config: Config,
    save_dir: Path | None = None,
    processes: int = psutil.cpu_count(),
    tiles: list[TileCoord] | None = None,
    zooms: list[int] | None = None,
    offset: Vector = Vector(0, 0),
    part1_batch_size: int = 8,
    part1_chunk_size: int = 8,
    part1_serial: bool = False,
    part3_batch_size: int = psutil.cpu_count(),
    part3_serial: bool = False,
) -> dict[TileCoord, Image.Image]:
    """
    Renders tiles from given coordinates and zoom values.

    :param Pla2File components: a JSON of components
    :param config: The configuration of the renderer
    :param int save_dir: The directory to save tiles to, ``None`` to make it not save
    :param int processes: The number of processes to run for rendering
    :param tiles: a list of tiles to render
    :param zooms: a list of zooms to render
    :param offset: the offset to shift all node coordinates by, given as ``(x,y)``
    :param int part1_batch_size: The batch size for part 1
    :param int part1_chunk_size: The chunk size for part 1
    :param int part1_serial: Whether part 1 will be run serially
    :param int part3_batch_size: The batch size for part 3
    :param int part3_serial: Whether part 3 will be run serially

    :returns: Given in the form of ``{tile_coord: image}``
    :rtype: dict[TileCoord, Image.Image]
    """

    log.debug("Creating save & temp directories")
    if save_dir is not None:
        save_dir.mkdir(exist_ok=True)
    config.temp_dir.mkdir(exist_ok=True)

    prepare_render(components, config, tiles, zooms, offset)

    if not part1_serial:
        log.info(f"Initialising Ray with {processes=}...")
        ray.init(num_cpus=processes)

    render_part1(
        config,
        part1_batch_size,
        part1_chunk_size,
        part1_serial,
    )
    render_part2(config)
    return render_part3(config, save_dir, part3_serial, part3_batch_size)
