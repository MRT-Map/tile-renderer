from pathlib import Path

from tile_renderer import Skin, render_tiles
from tile_renderer.types.pla2 import Pla2File


def main():
    a = Pla2File.from_file(Path(__file__).parent / "enc.pla2.msgpack")
    skin = Skin.default()
    # (Path(__file__).parent / "out.svg").write_text(str(render_svg(a.components, skin, 0)))
    Path("/tmp/tile-renderer").mkdir(exist_ok=True)
    for tile, b in render_tiles(a.components, skin, 0, 32, 256).items():
        Path(f"/tmp/tile-renderer/{tile}.png").write_bytes(b)


if __name__ == "__main__":
    main()
