from __future__ import annotations

import gc
import glob
import re
from dataclasses import dataclass, field
from itertools import chain
from typing import TYPE_CHECKING

import dill
from PIL import Image, ImageDraw
from rich.progress import track

from .._internal.logger import log
from ..misc_types.config import Config
from ..misc_types.coord import TileCoord, WorldCoord
from ..skin_type.line import LineBack, LineFore
from .multiprocess import MultiprocessConfig, ProgressHandler, multiprocess
from .utils import part_dir, wip_tiles_dir

if TYPE_CHECKING:
    from ray.types import ObjectRef

    from ..misc_types.pla2 import Component, Pla2File
    from ..skin_type import ComponentStyle, ComponentTypeInfo


@dataclass(frozen=True, init=True)
class Part1Consts(Config):
    """The constants used for part 1"""

    coord_to_comp: dict[WorldCoord, list[Component]] = field(default_factory=dict)
    """A dictionary of world coordinates to the components that have nodes at said coordinate"""

    @classmethod
    def from_config(
        cls,
        config: Config,
        coord_to_comp: dict[WorldCoord, list[Component]],
    ) -> Part1Consts:
        return cls(
            zoom=config.zoom,
            export_id=config.export_id,
            assets_dir=config.assets_dir,
            skin=config.skin,
            temp_dir=config.temp_dir,
            coord_to_comp=coord_to_comp,
        )


def render_part1(
    config: Config,
    mp_config: MultiprocessConfig = MultiprocessConfig(),  # noqa: B008
) -> None:
    """Part 1 of the rendering job. Check render() for the full list of parameters"""
    tile_coords = []
    with (part_dir(config, 0) / "processed.dill").open("rb") as f:
        data: tuple[Pla2File, int] = dill.load(f)  # noqa: S301
        components, operations = data

    for file in glob.glob(str(part_dir(config, 0) / "tile_*.dill")):
        re_result = re.search(r"tile_(-?\d+), (-?\d+), (-?\d+)\.dill$", file)
        if re_result is None:
            raise ValueError("Dill object not saved properly")
        tile_coords.append(
            TileCoord(
                int(re_result.group(1)),
                int(re_result.group(2)),
                int(re_result.group(3)),
            ),
        )

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
        f"Rendering components in {len(tile_coords)} tiles ({operations} operations)...",
    )

    multiprocess(
        tile_coords,
        consts,
        _pre_draw_components,
        "[green]Rendering components",
        operations,
        mp_config,
    )


def _pre_draw_components(
    ph: ObjectRef[ProgressHandler[TileCoord]] | None,
    tile_coord: TileCoord,
    consts: Part1Consts,
) -> None:
    path = part_dir(consts, 0) / f"tile_{tile_coord}.dill"
    with path.open("rb") as f:
        tile_components = dill.load(f)  # noqa: S301

    _draw_components(ph, tile_coord, tile_components, consts)

    path.unlink(missing_ok=True)
    with (part_dir(consts, 1) / f"tile_{tile_coord}.dill").open(
        "wb",
    ) as f:
        dill.dump(tile_coord, f)


def _draw_components(
    ph: ObjectRef[ProgressHandler[TileCoord]] | None,
    tile_coord: TileCoord,
    tile_components: list[list[Component]],
    consts: Part1Consts,
) -> None:
    img = Image.new(
        mode="RGBA",
        size=(consts.skin.tile_size,) * 2,
        color=consts.skin.background,
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
                    ph.add.remote(tile_coord)

            if _needs_con_rendering(type_info, step):
                step: LineBack  # noqa: PLW2901
                _render_con(tile_coord, consts, group, step, img)

                if ph:
                    ph.add.remote(tile_coord)

    img.save(
        wip_tiles_dir(consts) / f"{tile_coord}.png",
        "png",
    )


def _needs_con_rendering(type_info: ComponentTypeInfo, step: ComponentStyle) -> bool:
    return (
        type_info.shape == "line"
        and "road" in type_info.tags
        and isinstance(step, LineBack)
    )


def _render_con(
    tile_coord: TileCoord,
    consts: Part1Consts,
    group: list[Component],
    step: LineBack,
    img: Image.Image,
) -> None:
    coord: WorldCoord
    for coord in chain(*(c.nodes.coords for c in group)):
        con_img_coord = coord.to_image_coord(tile_coord, consts)

        for con_component in consts.coord_to_comp[coord]:
            if "road" not in consts.skin[con_component.type].tags:
                continue

            inter = Image.new("RGBA", (consts.skin.tile_size,) * 2, (0,) * 4)
            con_info = consts.skin[con_component.type]
            for con_step in con_info[consts.zoom.max - tile_coord.z]:
                if not isinstance(con_step, LineFore) or isinstance(con_step, LineBack):
                    continue

                con_img = Image.new("RGBA", (consts.skin.tile_size,) * 2, (0,) * 4)
                con_imd = ImageDraw.Draw(con_img)
                con_step.render(
                    con_component,
                    con_imd,
                    con_img,
                    consts,
                    tile_coord,
                )

                con_mask_img = Image.new("RGBA", (consts.skin.tile_size,) * 2, (0,) * 4)
                con_mask_imd = ImageDraw.Draw(con_mask_img)
                con_mask_imd.ellipse(
                    (
                        con_img_coord.x - max(con_step.width, step.width) + 1,
                        con_img_coord.y - max(con_step.width, step.width) + 1,
                        con_img_coord.x + max(con_step.width, step.width),
                        con_img_coord.y + max(con_step.width, step.width),
                    ),
                    fill="#000000",
                )

                inter.paste(con_img, (0, 0), con_mask_img)
            img.paste(inter, (0, 0), inter)
