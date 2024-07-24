import ctypes
import multiprocessing
import multiprocessing.sharedctypes
import os
import platform
import re
import subprocess
import tempfile
from pathlib import Path
from typing import cast

import rich
from rich.progress import Progress

from tile_renderer.coord import ORIGIN, Coord, TileCoord
from tile_renderer.pla2 import Component
from tile_renderer.render_svg import render_svg
from tile_renderer.skin import Skin


def _f(args):
    return _export_tile(*args)


def render_tiles(
    components: list[Component],
    skin: Skin,
    zoom: int,
    max_zoom_range: int,
    tile_size: int,
    offset: Coord = ORIGIN,
    processes: int = os.cpu_count() * 2,
    chunk_size: int = 8,
) -> dict[TileCoord, bytes]:
    images = {}
    doc = render_svg(components, skin, zoom)
    tiles = {t for c in components for t in c.tiles(zoom, max_zoom_range)}

    font_dir = Path(tempfile.gettempdir()) / "tile-renderer" / "fonts"
    font_dir.mkdir(exist_ok=True, parents=True)
    for i, (ext, file) in enumerate(skin.font_files):
        (font_dir / (str(i) + "." + ext)).write_bytes(file)

    with (
        multiprocessing.Pool(processes=processes) as pool,
        Progress() as progress,
        multiprocessing.Manager() as manager,
    ):
        task_id = progress.add_task("[green]Exporting to PNG", total=len(tiles))
        doc = re.sub(
            r'<svg width=".*?" height=".*?"',
            f'<svg viewBox="<|min_x|> <|min_y|> {max_zoom_range*2**zoom} {max_zoom_range*2**zoom}"',
            _simplify_svg(str(doc), font_dir, tile_size),
        )

        doc = manager.Value(ctypes.c_wchar_p, doc, lock=False)
        resvg_path = subprocess.check_output(["where" if platform.system() == "Windows" else "which", "resvg"]).strip()
        for i, (tile, b) in enumerate(
            pool.imap(
                _f,
                (
                    (
                        doc,
                        tile,
                        max_zoom_range,
                        offset,
                        str(skin.background),
                        font_dir,
                        tile_size,
                        resvg_path,
                    )
                    for tile in tiles
                ),
                chunk_size,
            )
        ):
            images[tile] = b
            progress.advance(task_id)
            if i % 10 == 0:
                progress.console.print(f"{i}/{len(tiles)}")
    return images


def _simplify_svg(doc: str, font_dir: Path, tile_size: int) -> str:
    usvg_path = subprocess.check_output(["where" if platform.system() == "Windows" else "which", "usvg"]).strip()
    p = subprocess.Popen(
        [
            usvg_path,
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--skip-system-fonts",
            "--use-fonts-dir",
            str(font_dir),
            "--default-width",
            str(tile_size),
            "--default-height",
            str(tile_size),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate(input=doc.encode("utf-8"))
    if err:
        rich.print("[yellow]" + err.decode("utf-8"))
    return out.decode("utf-8")


def _export_tile(
    doc: multiprocessing.sharedctypes.Synchronized,
    tile: TileCoord,
    max_zoom_range: int,
    offset: Coord,
    background: str,
    font_dir: Path,
    tile_size: int,
    resvg_path: str,
) -> tuple[TileCoord, bytes]:
    bounds = tile.bounds(max_zoom_range)
    doc = (
        cast(str, doc.value)
        .replace("<|min_x|>", str((bounds.x_min + offset.x)), 1)
        .replace("<|min_y|>", str((bounds.y_min + offset.y)), 1)
    )
    p = subprocess.Popen(
        [
            resvg_path,
            "-",
            "-c",
            "--resources-dir",
            Path(__file__).parent,
            "--background",
            background,
            "--skip-system-fonts",
            "--use-fonts-dir",
            str(font_dir),
            "--width",
            str(tile_size),
            "--height",
            str(tile_size),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate(input=doc.encode("utf-8"))
    if err:
        rich.print("[yellow]" + err.decode("utf-8"))
    return tile, out
