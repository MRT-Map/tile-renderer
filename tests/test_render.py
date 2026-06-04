# noqa: INP001
import sys
import time
from pathlib import Path

import rich

from tile_renderer.pla2 import Pla2File
from tile_renderer.render_svg import render_svg
from tile_renderer.render_tiles import render_tiles
from tile_renderer.skin import Skin


def main():
    pla2 = Pla2File.from_file(Path(__file__).parent / "kze.pla2.msgpack")
    skin = Skin.default()

    suffix = sys.argv[1]
    zoom_levels = [int(a) for a in sys.argv[2:]] or [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    if suffix == "png":
        Path("/tmp/tile-renderer").mkdir(exist_ok=True)
        for zoom in zoom_levels:
            for tile, b in render_tiles(pla2.components, skin, zoom, 32, 256).items():
                Path(f"/tmp/tile-renderer/{tile}.png").write_bytes(b)
    elif suffix == "svg":
        for zoom in zoom_levels:
            (Path(__file__).parent / f"out{zoom}.svg").write_text(str(render_svg(pla2.components, skin, zoom)))
    else:
        raise ValueError(f"Invalid suffix {suffix}")


if __name__ == "__main__":
    time_start = time.perf_counter()
    main()
    time_end = time.perf_counter()
    rich.print(f"Took {time_end - time_start} s")
