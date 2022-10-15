from __future__ import annotations

import glob
import os
import pickle
import re
from pathlib import Path

from rich.progress import Progress, track
from shapely.geometry import Polygon

from renderer.internals.logger import log
from renderer.types.coord import TileCoord, WorldCoord
from renderer.types.skin import _TextObject


def render_part2(
    export_id: str, temp_dir: Path = Path.cwd() / "temp"
) -> tuple[dict[TileCoord, list[_TextObject]], int]:
    zooms = set()
    log.info("Determining zoom levels...")
    for file in glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.1.pkl")):
        zoom = re.search(r"_(\d+),", file).group(1)
        zooms.add(zoom)

    all_new_texts = {}
    all_total_texts = 0
    with Progress() as progress:
        for zoom in progress.track(
            zooms, description="[green]Eliminating overlapping text"
        ):
            in_ = {}
            for file in progress.track(
                glob.glob(str(temp_dir / f"{glob.escape(export_id)}_{zoom},*.1.pkl")),
                description="Loading data",
            ):
                with open(file, "rb") as f:
                    in_.update(pickle.load(f))
            new_texts = _prevent_text_overlap(zoom, in_, progress)
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
    zoom: int, texts: dict[TileCoord, list[_TextObject]], progress: Progress
) -> dict[TileCoord, list[_TextObject]]:
    out = {}
    text_dict: dict[_TextObject, list[TileCoord]] = {}
    prep_id = progress.add_task(
        f"Zoom {zoom}: [dim white]Preparing text", total=len(texts)
    )
    for tile_coord, text_objects in texts.items():
        if tile_coord.z != zoom:
            continue
        for text in text_objects:
            text_dict.setdefault(text, []).append(tile_coord)
        progress.advance(prep_id, 1)
    progress.update(prep_id, visible=False)

    no_intersect: list[tuple[WorldCoord]] = []
    operations = len(text_dict)
    filter_id = progress.add_task(
        f"Zoom {zoom}: [dim white]Filtering text", total=operations
    )
    for i, text in enumerate(text_dict.copy().keys()):
        is_rendered = True
        for other in no_intersect:
            for bound in text.bounds:
                if Polygon(bound).intersects(Polygon(other)):
                    is_rendered = False
                    del text_dict[text]
                    break
                if not is_rendered:
                    break
            if not is_rendered:
                break
        progress.advance(filter_id, 1)
    progress.update(filter_id, visible=False)

    operations = len(text_dict)
    sort_id = progress.add_task(
        f"Zoom {zoom}: [dim white]Sorting remaining text", total=operations
    )
    for i, (text, tile_coords) in enumerate(text_dict.items()):
        for tile_coord in tile_coords:
            if tile_coord not in out:
                out[tile_coord] = []
            out[tile_coord].append(text)
        progress.advance(sort_id, 1)

    default = {tc: [] for tc in texts.keys()}
    return {**default, **out}
