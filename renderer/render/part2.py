from __future__ import annotations

import glob
import os
import pickle
from pathlib import Path

from rich.progress import Progress, track
from shapely.geometry import Polygon

from renderer.types.coord import TileCoord, WorldCoord
from renderer.types.skin import _TextObject


def render_part2(
    export_id: str, temp_dir: Path
) -> tuple[dict[TileCoord, list[_TextObject]], int]:
    in_ = {}
    for file in track(
        glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.1.pkl")),
        description="Loading data",
    ):
        with open(file, "rb") as f:
            in_.update(pickle.load(f))
    new_texts = _prevent_text_overlap(in_)
    total_texts = sum(len(t) for t in new_texts.values())
    with open(temp_dir / f"{export_id}.2.pkl", "wb") as f:
        pickle.dump((new_texts, total_texts), f)
    for file in track(
        glob.glob(str(temp_dir / f"{glob.escape(export_id)}_*.1.pkl")),
        description="Loading data",
    ):
        os.remove(file)
    return new_texts, total_texts


def _prevent_text_overlap(
    texts: dict[TileCoord, list[_TextObject]]
) -> dict[TileCoord, list[_TextObject]]:
    out = {}
    with Progress() as progress:
        zoom_id = progress.add_task(
            "[green]Eliminating overlapping text",
            total=len(zooms := set(c.z for c in texts.keys())),
        )
        for z in zooms:
            z: int
            text_dict: dict[_TextObject, list[TileCoord]] = {}
            prep_id = progress.add_task(
                f"Zoom {z}: [dim white]Preparing text", total=len(texts)
            )
            for tile_coord, text_objects in texts.items():
                if tile_coord.z != z:
                    continue
                for text in text_objects:
                    if text not in text_dict:
                        text_dict[text] = []
                    text_dict[text].append(tile_coord)
                progress.advance(prep_id, 1)
            progress.update(prep_id, visible=False)

            no_intersect: list[tuple[WorldCoord]] = []
            operations = len(text_dict)
            filter_id = progress.add_task(
                f"Zoom {z}: [dim white]Filtering text", total=operations
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
                f"Zoom {z}: [dim white]Sorting remaining text", total=operations
            )
            for i, (text, tile_coords) in enumerate(text_dict.items()):
                for tile_coord in tile_coords:
                    if tile_coord not in out:
                        out[tile_coord] = []
                    out[tile_coord].append(text)
                progress.advance(sort_id, 1)

            progress.advance(zoom_id, 1)
        default = {tc: [] for tc in texts.keys()}
    return {**default, **out}
