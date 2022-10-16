from __future__ import annotations

import functools
import itertools
import math
import os
import uuid
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
from uuid import UUID

import ray
from PIL import Image, ImageDraw
from shapely import LineString, Polygon

from renderer import math_utils
from renderer.types.coord import Coord, ImageCoord, TileCoord


@ray.remote
class ProgressHandler:
    def __init__(self):
        self.queue = Queue()
        self.completed = Queue()
        self.new_tasks_needed = Queue()

    def add(self, id_: TileCoord):
        self.queue.put_nowait(id_)

    def get(self) -> TileCoord | None:
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def complete(self, id_: TileCoord):
        self.completed.put_nowait(id_)

    def get_complete(self) -> TileCoord | None:
        try:
            return self.completed.get_nowait()
        except Empty:
            return None

    def request_new_task(self):
        self.new_tasks_needed.put_nowait(None)

    def needs_new_task(self) -> bool:
        try:
            self.queue.get_nowait()
            return True
        except Empty:
            return False


@dataclass(eq=True, unsafe_hash=True)
class _TextObject:
    image: list[UUID]
    center: list[ImageCoord]
    bounds: list[Polygon]
    temp_dir: Path = Path.cwd() / "temp"  # TODO

    @staticmethod
    def img_to_uuid(img: Image.Image, temp_dir: Path) -> UUID:
        u = uuid.uuid4()
        img.save(temp_dir / f"to.{u}.png")
        return u

    @staticmethod
    def uuid_to_img(u: UUID, temp_dir: Path) -> Image.Image:
        img = Image.open(temp_dir / f"to.{u}.png")
        os.remove(temp_dir / f"to.{u}.png")
        return img

    def __init__(
        self,
        image: Image.Image,
        x: float,
        y: float,
        w: float,
        h: float,
        rot: float,
        tile_coord: TileCoord,
        tile_size: int,
        imd: ImageDraw,
        debug: bool = False,
        temp_dir: Path = Path.cwd() / "temp",
    ):
        if debug:
            nr = functools.partial(
                math_utils.rotate_around_pivot, pivot=Coord(x, y), theta=-rot
            )
            imd.line(
                [
                    nr(x - w / 2, y - h / 2),
                    nr(x - w / 2, y + h / 2),
                    nr(x + w / 2, y + h / 2),
                    nr(x + w / 2, y - h / 2),
                    nr(x - w / 2, y - h / 2),
                ],
                fill="#ff0000",
            )
        self.temp_dir = temp_dir
        rot *= math.pi / 180
        r = functools.partial(
            math_utils.rotate_around_pivot,
            pivot=Coord(tile_coord.x * tile_size + x, tile_coord.y * tile_size + y),
            theta=-rot,
        )
        self.image = [_TextObject.img_to_uuid(image, temp_dir)]
        self.center = [
            ImageCoord(tile_coord.x * tile_size + x, tile_coord.y * tile_size + y),
        ]
        self.bounds = [
            Polygon(
                LineString(
                    [
                        r(
                            Coord(
                                tile_coord.x * tile_size + x - w / 2,
                                tile_coord.y * tile_size + y - h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                tile_coord.x * tile_size + x - w / 2,
                                tile_coord.y * tile_size + y + h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                tile_coord.x * tile_size + x + w / 2,
                                tile_coord.y * tile_size + y + h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                tile_coord.x * tile_size + x + w / 2,
                                tile_coord.y * tile_size + y - h / 2,
                            )
                        ).point,
                        r(
                            Coord(
                                tile_coord.x * tile_size + x - w / 2,
                                tile_coord.y * tile_size + y - h / 2,
                            )
                        ).point,
                    ]
                )
            )
        ]

    @classmethod
    def from_multiple(cls, *textobject: _TextObject):
        to = copy(textobject[0])

        to.bounds = list(itertools.chain(*[sto.bounds for sto in textobject]))
        to.image = list(itertools.chain(*[sto.image for sto in textobject]))
        to.center = list(itertools.chain(*[sto.center for sto in textobject]))

        return to
