from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID

    from ..misc_types.config import Config


def wip_tiles_dir(config: Config) -> Path:
    """
    Retrieve the directory for half-complete tiles
    """
    p = config.temp_dir / config.export_id / "wip_tiles"
    p.mkdir(parents=True, exist_ok=True)
    return p


def part_dir(config: Config, part: int) -> Path:
    """
    Retrieve the directory for data from each of the parts
    """
    p = config.temp_dir / config.export_id / str(part)
    p.mkdir(parents=True, exist_ok=True)
    return p


def text_object_path(config: Config, id_: UUID) -> Path:
    """
    Retrieve the directory for a text object
    """
    dir1 = id_.hex[0:2]
    dir2 = id_.hex[2:4]
    dir3 = id_.hex[4:6]
    dir4 = id_.hex[6:8]
    rest = id_.hex[8:] + ".png"
    dir_ = config.temp_dir / config.export_id / "to" / dir1 / dir2 / dir3 / dir4
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_ / rest
