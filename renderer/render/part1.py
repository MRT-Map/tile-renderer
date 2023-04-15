from __future__ import annotations

import gc
import glob
import logging
import os
import re
from dataclasses import dataclass, field
from itertools import chain

import dill
from PIL import Image, ImageDraw
from ray import ObjectRef
from rich.progress import track

from .._internal.logger import log
from ..misc_types.config import Config
from ..misc_types.coord import TileCoord, WorldCoord
from ..misc_types.pla2 import Component, Pla2File
from ..misc_types.skin import LineBack, LineFore
from .multiprocess import MultiprocessConfig, ProgressHandler, multiprocess
from .utils import part_dir, wip_tiles_dir


@dataclass(frozen=True, init=True)
class Part1Consts(Config):
    """The constants used for part 1"""

    coord_to_comp: dict[WorldCoord, list[Component]] = field(default_factory=dict)

    @classmethod
    def from_config(
        cls, config: Config, coord_to_comp: dict[WorldCoord, list[Component]]
    ) -> Part1Consts:
        return cls(
            zoom=config.zoom,
            export_id=config.export_id,
            assets_dir=config.assets_dir,
            skin=config.skin,
            temp_dir=config.temp_dir,
            coord_to_comp=coord_to_comp,
        )


def render_part1(config: Config, mp_config: MultiprocessConfig = MultiprocessConfig()):
    """Part 1 of the rendering job. Check render() for the full list of parameters"""
    tile_coords = []
    with open(part_dir(config, 0) / f"processed.dill", "rb") as f:
        components: Pla2File = dill.load(f)

    for file in glob.glob(str(part_dir(config, 0) / f"tile_*.dill")):
        re_result = re.search(rf"tile_(-?\d+), (-?\d+), (-?\d+)\.dill$", file)
        if re_result is None:
            raise ValueError("Dill object not saved properly")
        tile_coords.append(
            TileCoord(
                int(re_result.group(1)),
                int(re_result.group(2)),
                int(re_result.group(3)),
            )
        )

    operations = _count_num_rendering_ops(config)
    gc.collect()

    coord_to_comp: dict[WorldCoord, list[Component]] = {}
    for comp in track(components.components, "Generating coord_to_comp"):
        for node in comp.nodes:
            coord_to_comp.setdefault(node, []).append(comp)

    consts = Part1Consts.from_config(
        config,
        coord_to_comp,
    )

    log.info(
        f"Rendering components in {len(tile_coords)} tiles ({sum(operations.values())} operations)..."
    )

    multiprocess(
        tile_coords,
        consts,
        _pre_draw_components,
        "[green]Rendering components",
        sum(operations.values()),
        mp_config,
    )


def _pre_draw_components(
    ph: ObjectRef[ProgressHandler[TileCoord]] | None,  # type: ignore
    tile_coord: TileCoord,
    consts: Part1Consts,
) -> None:
    logging.getLogger("fontTools").setLevel(logging.CRITICAL)
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    path = part_dir(consts, 0) / f"tile_{tile_coord}.dill"
    with open(path, "rb") as f:
        tile_components = dill.load(f)

    _draw_components(ph, tile_coord, tile_components, consts)

    os.remove(path)
    with open(
        part_dir(consts, 1) / f"tile_{tile_coord}.dill",
        "wb",
    ) as f:
        dill.dump(tile_coord, f)


def _count_num_rendering_ops(config: Config) -> dict[TileCoord, int]:
    grouped_tile_list: dict[TileCoord, list[list[Component]]] = {}
    for file in track(
        glob.glob(str(part_dir(config, 0) / f"tile_*.dill")),
        description="Loading data",
    ):
        with open(file, "rb") as f:
            result = re.search(rf"tile_(-?\d+), (-?\d+), (-?\d+)\.dill$", file)
            if result is None:
                raise ValueError("Dill object is not saved properly")
            grouped_tile_list[
                TileCoord(
                    int(result.group(1)), int(result.group(2)), int(result.group(3))
                )
            ] = dill.load(f)

    tile_operations = 0
    operations = {}

    tile_coord: TileCoord
    tile_components: list[list[Component]]
    for tile_coord, tile_components in track(
        grouped_tile_list.items(), description="Counting operations"
    ):
        if not tile_components:
            operations[tile_coord] = 0
            continue

        for group in tile_components:
            if not group:
                continue
            info = config.skin.misc_types[group[0].type]
            for step in info[config.zoom.max - tile_coord.z]:
                tile_operations += len(group)
                if (
                    info.shape == "line"
                    and "road" in info.tags
                    and step.layer == "back"
                ):
                    tile_operations += 1

        operations[tile_coord] = tile_operations
        tile_operations = 0
    return operations


def _draw_components(
    ph: ObjectRef[ProgressHandler[TileCoord]] | None,  # type: ignore
    tile_coord: TileCoord,
    tile_components: list[list[Component]],
    consts: Part1Consts,
):
    img = Image.new(
        mode="RGBA", size=(consts.skin.tile_size,) * 2, color=consts.skin.background
    )
    imd = ImageDraw.Draw(img)

    for group in tile_components:
        type_info = consts.skin[group[0].type]
        style = type_info[consts.zoom.max - tile_coord[0]]
        for step in style:
            for component in group:
                step.render(
                    component,
                    imd,
                    img,
                    consts,
                    tile_coord,
                )

                if ph:
                    ph.add.remote(tile_coord)  # type: ignore

            if (
                type_info.shape == "line"
                and "road" in type_info.tags
                and isinstance(step, LineBack)
            ):
                coord: WorldCoord
                for coord in chain(*(c.nodes.coords for c in group)):
                    con_img_coord = coord.to_image_coord(tile_coord, consts)

                    for con_component in consts.coord_to_comp[coord]:
                        if "road" not in consts.skin[con_component.type].tags:
                            continue

                        inter = Image.new(
                            "RGBA", (consts.skin.tile_size,) * 2, (0,) * 4
                        )
                        con_info = consts.skin[con_component.type]
                        for con_step in con_info[consts.zoom.max - tile_coord.z]:
                            if not isinstance(con_step, LineFore) or isinstance(
                                con_step, LineBack
                            ):
                                continue

                            con_img = Image.new(
                                "RGBA", (consts.skin.tile_size,) * 2, (0,) * 4
                            )
                            con_imd = ImageDraw.Draw(con_img)
                            con_step.render(
                                con_component,
                                con_imd,
                                con_img,
                                consts,
                                tile_coord,
                            )

                            con_mask_img = Image.new(
                                "RGBA", (consts.skin.tile_size,) * 2, (0,) * 4
                            )
                            con_mask_imd = ImageDraw.Draw(con_mask_img)
                            con_mask_imd.ellipse(
                                (
                                    con_img_coord.x
                                    - max(con_step.width, step.width)
                                    + 1,
                                    con_img_coord.y
                                    - max(con_step.width, step.width)
                                    + 1,
                                    con_img_coord.x + max(con_step.width, step.width),
                                    con_img_coord.y + max(con_step.width, step.width),
                                ),
                                fill="#000000",
                            )

                            inter.paste(con_img, (0, 0), con_mask_img)
                        img.paste(inter, (0, 0), inter)

                if ph:
                    ph.add.remote(tile_coord)  # type: ignore

    img.save(
        wip_tiles_dir(consts) / f"{tile_coord}.png",
        "png",
    )
    if ph:
        ph.complete.remote(tile_coord)  # type: ignore
