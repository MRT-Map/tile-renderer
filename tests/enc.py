from pathlib import Path

from tile_renderer import Skin, render
from tile_renderer.types.pla2 import Pla2File


def main():
    a = Pla2File.from_file(Path(__file__).parent / "enc.pla2.msgpack")
    skin = Skin.default()
    Path("/tmp/tile-renderer").mkdir(exist_ok=True)
    for tile, b in render(a.components, skin, {0}, 256).items():
        Path(f"/tmp/tile-renderer/{tile}.png").write_bytes(b)


if __name__ == "__main__":
    main()
