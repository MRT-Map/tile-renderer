from pathlib import Path

from tile_renderer.types.pla2 import Pla2File

a = Pla2File.from_file(Path(__file__).parent / "enc.pla2.msgpack")
for c in a:
    print(c)
