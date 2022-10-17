from __future__ import annotations

import glob
import os
import re
from itertools import product
from pathlib import Path
from typing import Any, Generator

import dill
from rich.progress import Progress
from shapely import prepare
from shapely.geometry import Polygon

from renderer.internals.logger import log
from renderer.render.utils import _TextObject, part_dir
from renderer.types.coord import TileCoord


def file_loader(
    zoom: int, temp_dir: Path, export_id: str
) -> Generator[tuple[TileCoord, list[_TextObject]], Any, None]:
    for file in glob.glob(
        str(part_dir(temp_dir, export_id, 1) / f"tile_{zoom},*.dill")
    ):
        with open(file, "rb") as f:
            data = dill.load(f)
        for tile_coord, text_objects in data.items():
            yield tile_coord, text_objects


def render_part2(
    export_id: str, temp_dir: Path = Path.cwd() / "temp"
) -> tuple[dict[TileCoord, list[_TextObject]], int]:
    zooms = {}
    log.info("Determining zoom levels...")
    for file in glob.glob(str(part_dir(temp_dir, export_id, 1) / f"tile_*.dill")):
        zoom = re.search(r"_(\d+),", file).group(1)
        if zoom not in zooms:
            zooms[zoom] = 0
        zooms[zoom] += 1

    all_new_texts = {}
    all_total_texts = 0
    with Progress() as progress:
        for zoom, length in progress.track(
            zooms.items(), description="[green]Eliminating overlapping text"
        ):
            new_texts = _prevent_text_overlap(
                zoom,
                file_loader(zoom, temp_dir, export_id),
                length,
                progress,
                temp_dir,
                export_id,
            )
            total_texts = sum(len(t) for t in new_texts.values())
            with open(part_dir(temp_dir, export_id, 2) / f"{zoom}.dill", "wb") as f:
                dill.dump((new_texts, total_texts), f)
            for file in progress.track(
                glob.glob(
                    str(part_dir(temp_dir, export_id, 1) / f"tile_{zoom},*.dill")
                ),
                description="Cleaning up",
            ):
                os.remove(file)
            all_new_texts.update(new_texts)
            all_total_texts += total_texts
    return all_new_texts, all_total_texts


def _prevent_text_overlap(
    zoom: int,
    texts: Generator[tuple[TileCoord, list[_TextObject]], Any, None],
    length: int,
    progress: Progress,
    temp_dir: Path,
    export_id: str,
) -> dict[TileCoord, list[_TextObject]]:
    out = {}
    tile_coords = set()

    no_intersect: dict[TileCoord, set[Polygon]] = {}
    for tile_coord, text_objects in progress.track(
        texts, description=f"Zoom {zoom}: [dim white]Filtering text", total=length
    ):
        tile_coords.add(tile_coord)
        for text in text_objects:
            if not any(
                poly.intersects(ni)
                for ni in no_intersect.get(tile_coord, set())
                for poly in text.bounds
            ):
                for dx, dy in product((-1, 0, 1), (-1, 0, 1)):
                    tc = TileCoord(tile_coord.z, tile_coord.x + dx, tile_coord.y + dy)
                    out.setdefault(tc, []).append(text)
                    no_intersect.setdefault(
                        tc,
                        set(),
                    ).update(prepare(poly) for poly in text.bounds)
            else:
                for id_ in text.image:
                    _TextObject.remove_img(id_, temp_dir, export_id)

    default = {tc: [] for tc in tile_coords}
    return {**default, **out}
