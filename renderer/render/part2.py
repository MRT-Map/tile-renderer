from __future__ import annotations

import glob
import re
from pathlib import Path
from typing import TYPE_CHECKING

import dill
from PIL import Image, ImageDraw
from rich.progress import track
from shapely import prepare

from .._internal.logger import log
from ..skin_type.area import AreaBorderText, AreaCenterText
from ..skin_type.line import LineText
from ..skin_type.point import PointText
from .multiprocess import MultiprocessConfig, ProgressHandler, multiprocess
from .text_object import TextObject
from .utils import part_dir

if TYPE_CHECKING:
    from ray.types import ObjectRef
    from shapely.geometry import Polygon

    from ..misc_types.config import Config
    from ..misc_types.coord import TileCoord
    from ..misc_types.pla2 import Component, Pla2File


def render_part2(
    config: Config,
    mp_config1: MultiprocessConfig = MultiprocessConfig(),  # noqa: B008,
    mp_config2: MultiprocessConfig = MultiprocessConfig(),  # noqa: B008
) -> dict[TileCoord, list[TextObject]]:
    """Part 2 of the rendering job. Check render() for the full list of parameters"""
    zooms = set()
    log.info("Determining zoom levels...")
    for file in glob.glob(str(part_dir(config, 1) / "tile_*.dill")):
        regex = re.search(r"_(\d+),", file)
        if regex is None:
            raise ValueError("Dill object is not saved properly")
        zoom = regex.group(1)
        zooms.add(int(zoom))
    with (part_dir(config, 0) / "processed.dill").open("rb") as f:
        components: Pla2File = dill.load(f)[0]  # noqa: S301

    def key(comp: Component) -> int:
        return config.skin.order.index(comp.type)

    sorted_ = sorted(components.components, key=key, reverse=True)

    pre_text_objects = multiprocess(
        sorted_,
        (config, zooms),
        _find_text_objects,
        "[green]Finding text",
        len(components.components),
        mp_config1,
    )
    text_objects: dict[int, list[TextObject]] = {}
    for li in pre_text_objects:
        for z, to in li.items():
            text_objects.setdefault(z, []).extend(to)

    pre_result = multiprocess(
        [(a, b) for a, b in text_objects.items()],
        config,
        _prevent_text_overlap,
        "[green]Eliminating overlapping text",
        sum(len(to) for to in text_objects.values()),
        mp_config2,
    )
    result = {}
    for a in pre_result:
        result.update(a)

    for file in track(
        glob.glob(str(part_dir(config, 1) / "tile_*.dill")),
        description="Cleaning up",
    ):
        Path(file).unlink(missing_ok=True)
    (part_dir(config, 0) / "processed.dill").unlink(missing_ok=True)

    return result


def _find_text_objects(
    ph: ObjectRef[ProgressHandler[Component]] | None,
    component: Component,
    const_data: tuple[Config, set[int]],
) -> dict[int, list[TextObject]]:
    config, zooms = const_data
    type_info = config.skin[component.type]
    out: dict[int, list[TextObject]] = {}

    img = Image.new(
        mode="RGBA",
        size=(config.skin.tile_size,) * 2,
        color=config.skin.background,
    )
    imd = ImageDraw.Draw(img)

    for zoom in zooms:
        styles = type_info[config.zoom.max - zoom]
        for style in styles:
            if isinstance(
                style,
                PointText | LineText | AreaCenterText | AreaBorderText,
            ):
                out.setdefault(zoom, []).extend(
                    style.text(component, imd, config, zoom),
                )

    if ph:
        ph.add.remote(component.fid)

    return out


def _prevent_text_overlap(
    ph: ObjectRef[ProgressHandler[int]] | None,
    i: tuple[int, list[TextObject]],
    config: Config,
) -> dict[TileCoord, list[TextObject]]:
    zoom, texts = i

    out: list[TextObject] = []

    no_intersect: set[Polygon] = set()
    for text in texts:
        if not any(poly.intersects(ni) for ni in no_intersect for poly in text.bounds):
            out.append(text)
            for poly in text.bounds:
                prepare(poly)
            no_intersect.update(text.bounds)
        else:
            for id_ in text.image:
                TextObject.remove_img(id_, config)
        if ph:
            ph.add.remote(zoom)

    new_out: dict[TileCoord, list[TextObject]] = {}
    for text in out:
        for tile in text.to_tiles(config.zoom):
            if tile.z == zoom:
                new_out.setdefault(tile, []).append(text)

    for tile_coord, text_objects in new_out.items():
        with (part_dir(config, 2) / f"tile_{tile_coord}.dill").open("wb") as f:
            dill.dump(text_objects, f)

    return new_out
