from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import psutil
import ray
from PIL import Image

from .._internal.logger import log
from .multiprocess import MultiprocessConfig

if TYPE_CHECKING:
    from ..misc_types.config import Config
    from ..misc_types.pla2 import Pla2File

from ..misc_types.coord import TileCoord, Vector


def render(
    components: Pla2File,
    config: Config,
    save_dir: Path | None = None,
    processes: int = psutil.cpu_count(),
    tiles: list[TileCoord] | None = None,
    zooms: list[int] | None = None,
    offset: Vector = Vector(0, 0),
    part1_mp_config: MultiprocessConfig = MultiprocessConfig(),
    part2_mp_config1: MultiprocessConfig = MultiprocessConfig(),
    part2_mp_config2: MultiprocessConfig = MultiprocessConfig(),
    part3_mp_config: MultiprocessConfig = MultiprocessConfig(),
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
    :param part1_mp_config: The configuration for the processing of part 1
    :param part2_mp_config1: The configuration for the 1st processing of part 2
    :param part2_mp_config2: The configuration for the 2nd processing of part 2
    :param part3_mp_config: The configuration for the processing of part 3

    :returns: Given in the form of ``{tile_coord: image}``
    :rtype: dict[TileCoord, Image.Image]
    """

    log.debug("Creating save & temp directories")
    if save_dir is not None:
        save_dir.mkdir(exist_ok=True)
    config.temp_dir.mkdir(exist_ok=True)
    from .part1 import render_part1
    from .part2 import render_part2
    from .part3 import render_part3
    from .prepare import prepare_render

    prepare_render(components, config, tiles, zooms, offset)

    if (
        not part1_mp_config.serial
        and not part2_mp_config1.serial
        and not part2_mp_config2.serial
        and not part3_mp_config.serial
    ):
        log.info(f"Initialising Ray with {processes=}...")
        ray.init(num_cpus=processes)

    render_part1(config, part1_mp_config)
    render_part2(config, part2_mp_config1, part2_mp_config2)
    return render_part3(config, save_dir, part3_mp_config)
