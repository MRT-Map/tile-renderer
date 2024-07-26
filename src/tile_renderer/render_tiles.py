import multiprocessing
import multiprocessing.sharedctypes
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from tile_renderer._logger import log
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
    processes: int = (os.cpu_count() or 8) * 2,
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
    ):
        task_id = progress.add_task("Exporting to PNG", total=len(tiles), console=Console(file=sys.stderr))
        doc_str = re.sub(
            r'<svg width=".*?" height=".*?"',
            f'<svg viewBox="<|min_x|> <|min_y|> {max_zoom_range*2**zoom} {max_zoom_range*2**zoom}"',
            _simplify_svg(str(doc), font_dir, tile_size),
        )

        resvg_path = subprocess.check_output(["where" if platform.system() == "Windows" else "which", "resvg"]).strip()
        for i, (tile, b) in enumerate(
            pool.imap(
                _f,
                (
                    (
                        doc_str,
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
                log.info(f"{i}/{len(tiles)}")
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
    out, err = p.communicate(input=doc.encode())
    if err:
        log.warn("" + err.decode())
    return out.decode()


def _export_tile(
    doc: str,
    tile: TileCoord,
    max_zoom_range: int,
    offset: Coord,
    background: str,
    font_dir: Path,
    tile_size: int,
    resvg_path: str,
) -> tuple[TileCoord, bytes]:
    bounds = tile.bounds(max_zoom_range)
    doc = doc.replace("<|min_x|>", str(bounds.x_min + offset.x), 1).replace(
        "<|min_y|>", str(bounds.y_min + offset.y), 1
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
    out, err = p.communicate(input=doc.encode())
    if err:
        log.warn("" + err.decode())
    return tile, out
