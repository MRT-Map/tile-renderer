import sys
import time
from pathlib import Path

import rich

from tile_renderer.pla2 import Pla2File
from tile_renderer.render_svg import render_svg
from tile_renderer.render_tiles import render_tiles
from tile_renderer.skin import Skin


def main():
    a = Pla2File.from_file(Path(__file__).parent / "kze.pla2.msgpack")
    skin = Skin.default()
    if len(sys.argv) > 1:
        Path("/tmp/tile-renderer").mkdir(exist_ok=True)
        for zoom in (int(a) for a in sys.argv[1:]):
            for tile, b in render_tiles(a.components, skin, zoom, 32, 256).items():
                Path(f"/tmp/tile-renderer/{tile}.png").write_bytes(b)
    else:
        for zoom in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
            (Path(__file__).parent / f"out{zoom}.svg").write_text(str(render_svg(a.components, skin, zoom)))


if __name__ == "__main__":
    time_start = time.perf_counter()
    main()
    time_end = time.perf_counter()
    rich.print(f"Took {time_end - time_start} s")
