from pathlib import Path

from tile_renderer import Skin, render_svg
from tile_renderer.types.pla2 import Pla2File


def main():
    a = Pla2File.from_file(Path(__file__).parent / "enc.pla2.msgpack")
    skin = Skin.default()
    Path("out.svg").write_text(str(render_svg(a.components, skin, 0)))


if __name__ == "__main__":
    main()
