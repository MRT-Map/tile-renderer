from __future__ import annotations

import functools
import itertools
import uuid
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

from PIL import Image
from shapely import LineString, Polygon

from .. import math_utils
from ..misc_types.coord import ImageCoord, TileCoord, WorldCoord, WorldLine
from .utils import text_object_path

if TYPE_CHECKING:
    from ..misc_types.config import Config
    from ..misc_types.zoom_params import ZoomParams


@dataclass(eq=True, unsafe_hash=True)
class TextObject:
    """A text to be pasted into the map at part 3"""

    image: list[UUID]
    """A list of UUIDs, each representing an image in the temporary folder"""
    center: list[WorldCoord]
    """The centers of each image"""
    bounds: list[Polygon]
    """The bounds of the text in each image"""
    temp_dir: Path = Path.cwd() / "temp"
    """The temporary directory that the images belong to"""
    export_id: str = "unnamed"
    """The export ID of the render job"""

    @staticmethod
    def img_to_uuid(img: Image.Image, config: Config) -> UUID:
        """
        Puts the image into the temporary directory and returns the UUID corresponding to the image
        """
        u = uuid.uuid4()
        path = text_object_path(config, u)
        img.save(path)
        return u

    @staticmethod
    def uuid_to_img(u: UUID, config: Config) -> Image.Image:
        """
        Retrieves an image object, given its corresponding UUID

        :raises FileNotFoundError: if the UUID is invalid
        """
        path = text_object_path(config, u)
        return Image.open(path)

    @staticmethod
    def remove_img(u: UUID, config: Config) -> None:
        """
        Remove the image from the temporary directory

        :raises FileNotFoundError: If the UUID is invalid
        """
        path = text_object_path(config, u)
        path.unlink(missing_ok=True)

    def __init__(
        self,
        img: Image.Image,
        center: ImageCoord,
        width_height: tuple[float, float],
        rot: float,
        zoom: int,
        config: Config,
    ) -> None:
        """
        :param img: The Image object of the current tile
        :param center: The centre of the text
        :param width_height: The width and height of the text
        :param rot: The rotation of the text
        :param zoom: The zoom level of the text
        :param config: The configuration
        """
        w, h = width_height
        self.temp_dir = config.temp_dir
        self.export_id = config.export_id

        self.image = [TextObject.img_to_uuid(img, config)]
        self.center = [center.to_world_coord(TileCoord(zoom, 0, 0), config)]
        r = functools.partial(
            math_utils.rotate_around_pivot,
            pivot=center,
            theta=-rot,
        )
        bounds = [
            r(ImageCoord(center.x - w / 2, center.y - h / 2)),
            r(ImageCoord(center.x - w / 2, center.y + h / 2)),
            r(ImageCoord(center.x + w / 2, center.y + h / 2)),
            r(ImageCoord(center.x + w / 2, center.y - h / 2)),
            r(ImageCoord(center.x - w / 2, center.y - h / 2)),
        ]
        self.bounds = [
            Polygon(
                LineString(
                    ImageCoord(a.x, a.y)
                    .to_world_coord(TileCoord(zoom, 0, 0), config)
                    .as_tuple()
                    for a in bounds
                ),
            ),
        ]

    @classmethod
    def from_multiple(cls, *text_object: TextObject) -> TextObject:
        """Create a new compound TextObject from multiple TextObjects"""
        to = copy(text_object[0])

        to.bounds = list(itertools.chain(*[sto.bounds for sto in text_object]))
        to.image = list(itertools.chain(*[sto.image for sto in text_object]))
        to.center = list(itertools.chain(*[sto.center for sto in text_object]))

        return to

    def to_tiles(self, zoom: ZoomParams) -> list[TileCoord]:
        """Find the tiles that the text will be rendered in"""
        tiles = []
        for bound in self.bounds:
            tiles.extend(
                WorldLine(
                    [WorldCoord(x, y) for x, y in bound.exterior.coords],
                ).to_tiles(zoom),
            )
        return list(set(tiles))
