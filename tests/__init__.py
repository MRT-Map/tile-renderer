from pathlib import Path

from tile_renderer import Skin, render
from tile_renderer.types.pla2 import Pla2File

a = Pla2File.from_file(Path(__file__).parent / "enc.pla2.msgpack")
skin = Skin.default()
render(a.components, skin, {0})
