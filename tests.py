import sys
from random import randint

from renderer.misc_types.config import Config
from renderer.misc_types.coord import ImageCoord, TileCoord, WorldCoord
from renderer.misc_types.zoom_params import ZoomParams


def test_world_to_image():
    for _ in range(1000):
        x, y = randint(-1000, 1000), randint(-1000, 1000)
        z = randint(0, 16)
        r = randint(1, 1000)
        tx, ty = randint(-1000, 1000), randint(-1000, 1000)
        coord = WorldCoord(x, y)
        tile_coord = TileCoord(z, tx, ty)
        config = Config(ZoomParams(z, z, r))
        new_coord = coord.to_image_coord(tile_coord, config).to_world_coord(
            tile_coord, config
        )
        assert coord.x - new_coord.x < 1e10
        assert coord.y - new_coord.y < 1e10
