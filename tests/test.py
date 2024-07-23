import sys
import time
from pathlib import Path

import rich

from tile_renderer import Skin, render_svg, render_tiles
from tile_renderer.types.pla2 import Pla2File


def main():
    a = Pla2File.from_file(Path(__file__).parent / "kze.pla2.msgpack")
    skin = Skin.default()
    for zoom in (2, 3, 4, 5, 6, 7, 8, 9):
        if len(sys.argv) > 1 and sys.argv[1] == "png":
            Path("/tmp/tile-renderer").mkdir(exist_ok=True)
            for tile, b in render_tiles(a.components, skin, zoom, 32, 256).items():
                Path(f"/tmp/tile-renderer/{tile}.png").write_bytes(b)
        else:
            (Path(__file__).parent / f"out{zoom}.svg").write_text(str(render_svg(a.components, skin, zoom)))


if __name__ == "__main__":
    time_start = time.perf_counter()
    main()
    time_end = time.perf_counter()
    rich.print(f"Took {time_end - time_start} s")
