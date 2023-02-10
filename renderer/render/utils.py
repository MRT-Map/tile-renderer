from __future__ import annotations

import functools
import itertools
import os
import uuid
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
from typing import TYPE_CHECKING
from uuid import UUID

import ray
from PIL import Image, ImageDraw
from shapely import LineString, Polygon

from .. import math_utils
from ..misc_types.coord import Coord, ImageCoord, TileCoord, WorldCoord

if TYPE_CHECKING:
    from ..render.part1 import Part1Consts


@ray.remote
class ProgressHandler:
    """The handler for progress bars"""

    def __init__(self):
        self.queue = Queue()
        """The queue of TileCoords to be processed"""
        self.completed = Queue()
        """The list of completed TileCoords"""
        self.new_tasks_needed = Queue()
        """If this queue has something, a new task is needed"""

    def add(self, id_: TileCoord):
        """Add a TileCoord to the queue"""
        self.queue.put_nowait(id_)

    def get(self) -> TileCoord | None:
        """Get the first TileCoord in the queue"""
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def complete(self, id_: TileCoord):
        """Complete a TileCoord"""
        self.completed.put_nowait(id_)

    def get_complete(self) -> TileCoord | None:
        """Get the first completed TileCoord in the queue"""
        try:
            return self.completed.get_nowait()
        except Empty:
            return None

    def request_new_task(self):
        """Request a new task to be processed"""
        self.new_tasks_needed.put_nowait(None)

    def needs_new_task(self) -> bool:
        """Returns True if a new task is needed, and resets the value to False"""
        try:
            self.queue.get_nowait()
            return True
        except Empty:
            return False


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
    def img_to_uuid(img: Image.Image, temp_dir: Path, export_id: str) -> UUID:
        """
        Puts the image into the temporary directory and returns the UUID corresponding to the image

        :param img: The image to save
        :param temp_dir: The temporary directory to save into
        :param export_id: The export ID of the render job

        :return: The UUID
        """
        u = uuid.uuid4()
        path = text_object_path(temp_dir, export_id, u)
        img.save(path)
        return u

    @staticmethod
    def uuid_to_img(u: UUID, temp_dir: Path, export_id: str) -> Image.Image:
        """
        Retrieves an image object, given its corresponding UUID

        :param u: The UUID
        :param temp_dir: The temporary directory to save into
        :param export_id: The export ID of the render job

        :return: The image object
        :raises FileNotFoundError: if the UUID is invalid
        """
        path = text_object_path(temp_dir, export_id, u)
        img = Image.open(path)
        return img

    @staticmethod
    def remove_img(u: UUID, temp_dir: Path, export_id: str):
        """
        Remove the image from the temporary directory

        :param u: The UUID
        :param temp_dir: The temporary directory to save into
        :param export_id: The export ID of the render job

        :raises FileNotFoundError: if the UUID is invalid
        """
        path = text_object_path(temp_dir, export_id, u)
        os.remove(path)

    def __init__(
        self,
        img: Image.Image,
        imd: ImageDraw.ImageDraw,
        center: ImageCoord,
        width_height: tuple[float, float],
        rot: float,
        tile_coord: TileCoord,
        consts: Part1Consts,
    ):
        """
        :param img: The Image object of the current tile
        :param imd: The ImageDraw object of the current tile
        :param center: The centre of the text
        :param width_height: The width and height of the text
        :param rot: The rotation of the text
        :param tile_coord: The tile coordinate that the text belongs to
        :param consts: The constants of part 1
        """
        w, h = width_height
        if os.environ.get("DEBUG"):
            nr = functools.partial(
                math_utils.rotate_around_pivot, pivot=center, theta=-rot
            )
            imd.line(
                [
                    nr(Coord(center.x - w / 2, center.y - h / 2)).as_tuple(),
                    nr(Coord(center.x - w / 2, center.y + h / 2)).as_tuple(),
                    nr(Coord(center.x + w / 2, center.y + h / 2)).as_tuple(),
                    nr(Coord(center.x + w / 2, center.y - h / 2)).as_tuple(),
                    nr(Coord(center.x - w / 2, center.y - h / 2)).as_tuple(),
                ],
                fill="#ff0000",
            )
        self.temp_dir = consts.temp_dir
        self.export_id = consts.export_id

        self.image = [TextObject.img_to_uuid(img, consts.temp_dir, consts.export_id)]
        new_center = center.to_world_coord(consts.skin, tile_coord, consts.zoom)
        self.center = [new_center]
        r = functools.partial(
            math_utils.rotate_around_pivot,
            pivot=new_center,
            theta=-rot,
        )
        new_width_height = ImageCoord(w, h).to_world_coord(
            consts.skin, tile_coord, consts.zoom
        )
        w, h = new_width_height.x, new_width_height.y
        self.bounds = [
            Polygon(
                LineString(
                    [
                        r(
                            Coord(
                                new_center.x - w / 2,
                                new_center.y - h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                new_center.x - w / 2,
                                new_center.y + h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                new_center.x + w / 2,
                                new_center.y + h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                new_center.x + w / 2,
                                new_center.y - h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                new_center.x - w / 2,
                                new_center.y - h / 2,
                            )
                        ).point,
                    ]
                )
            )
        ]

    @classmethod
    def from_multiple(cls, *text_object: TextObject) -> TextObject:
        """Create a new compound TextObject from multiple TextObjects"""
        to = copy(text_object[0])

        to.bounds = list(itertools.chain(*[sto.bounds for sto in text_object]))
        to.image = list(itertools.chain(*[sto.image for sto in text_object]))
        to.center = list(itertools.chain(*[sto.center for sto in text_object]))

        return to


def wip_tiles_dir(temp_dir: Path, export_id: str) -> Path:
    """
    Retrieve the directory for half-complete tiles

    :param temp_dir: The temporary directory
    :param export_id: The export ID of the render job
    :return: The path of the directory
    """
    p = temp_dir / export_id / "wip_tiles"
    p.mkdir(parents=True, exist_ok=True)
    return p


def part_dir(temp_dir: Path, export_id: str, part: int) -> Path:
    """
    Retrieve the directory for data from each of the parts

    :param temp_dir: The temporary directory
    :param export_id: The export ID of the render job
    :param part: The part number (0, 1, 2)
    :return: The path of the directory
    """
    p = temp_dir / export_id / str(part)
    p.mkdir(parents=True, exist_ok=True)
    return p


def text_object_path(temp_dir: Path, export_id: str, id_: UUID) -> Path:
    """
    Retrieve the directory for a text object

    :param temp_dir: The temporary directory
    :param export_id: The export ID of the render job
    :param id_: The UUID of the text object

    :return: The path of the directory
    """
    dir1 = id_.hex[0:2]
    dir2 = id_.hex[2:4]
    dir3 = id_.hex[4:6]
    dir4 = id_.hex[6:8]
    rest = id_.hex[8:] + ".png"
    dir_ = temp_dir / export_id / "to" / dir1 / dir2 / dir3 / dir4
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_ / rest
