from __future__ import annotations

import glob
import os
import pickle
import re
from pathlib import Path
from typing import Any, Generator

from rich.progress import Progress
from shapely.geometry import Polygon

from renderer.internals.logger import log
from renderer.types.coord import TileCoord
from renderer.types.skin import _TextObject


def file_loader(
    zoom: int, temp_dir: Path, export_id: str
) -> Generator[tuple[TileCoord, list[_TextObject]], Any, None]:
    for file in glob.glob(str(temp_dir / f"{glob.escape(export_id)}_{zoom},*.1.pkl")):
        with open(file, "rb") as f:
            data = pickle.load(f)
        for tile_coord, text_objects in data.items():
            yield tile_coord, text_objects


def render_part2(
    export_id: str, temp_dir: Path = Path.cwd() / "temp"
) -> tuple[dict[TileCoord, list[_TextObject]], int]:
    zooms = {}
    log.info("Determining zoom levels...")
    for file in glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.1.pkl")):
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
                zoom, file_loader(zoom, temp_dir, export_id), length, progress
            )
            total_texts = sum(len(t) for t in new_texts.values())
        with open(temp_dir / f"{export_id}_{zoom}.2.pkl", "wb") as f:
            pickle.dump((new_texts, total_texts), f)
        for file in progress.track(
            glob.glob(str(temp_dir / f"{glob.escape(export_id)}_{zoom},*.1.pkl")),
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
) -> dict[TileCoord, list[_TextObject]]:
    out = {}
    tile_coords = set()

    no_intersect: list[Polygon] = []
    for tile_coord, text_objects in progress.track(
        texts, description=f"Zoom {zoom}: [dim white]Filtering text", total=length
    ):
        tile_coords.add(tile_coord)
        for text in text_objects:
            is_rendered = True
            polys = []
            for other in no_intersect:
                for bound in text.bounds:
                    poly = Polygon(bound)
                    if Polygon(bound).intersects(other):
                        is_rendered = False
                        break
                    polys.append(poly)
                if not is_rendered:
                    break
            if is_rendered:
                out.setdefault(tile_coord, []).append(text)
                no_intersect.extend(polys)

    default = {tc: [] for tc in tile_coords}
    return {**default, **out}
