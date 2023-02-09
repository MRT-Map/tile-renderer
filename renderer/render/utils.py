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
class TextObject:
    image: list[UUID]
    center: list[WorldCoord]
    bounds: list[Polygon]
    temp_dir: Path = Path.cwd() / "temp"  # TODO
    export_id: str = "unnamed"

    @staticmethod
    def img_to_uuid(img: Image.Image, temp_dir: Path, export_dir: str) -> UUID:
        u = uuid.uuid4()
        path = text_object_path(temp_dir, export_dir, u)
        img.save(path)
        return u

    @staticmethod
    def uuid_to_img(u: UUID, temp_dir: Path, export_id: str) -> Image.Image:
        path = text_object_path(temp_dir, export_id, u)
        img = Image.open(path)
        return img

    @staticmethod
    def remove_img(u: UUID, temp_dir: Path, export_id: str):
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
    def from_multiple(cls, *text_object: TextObject):
        to = copy(text_object[0])

        to.bounds = list(itertools.chain(*[sto.bounds for sto in text_object]))
        to.image = list(itertools.chain(*[sto.image for sto in text_object]))
        to.center = list(itertools.chain(*[sto.center for sto in text_object]))

        return to


def wip_tiles_dir(temp_dir: Path, export_id: str) -> Path:
    p = temp_dir / export_id / "wip_tiles"
    p.mkdir(parents=True, exist_ok=True)
    return p


def part_dir(temp_dir: Path, export_id: str, part: int) -> Path:
    p = temp_dir / export_id / str(part)
    p.mkdir(parents=True, exist_ok=True)
    return p


def text_object_path(temp_dir: Path, export_id: str, id_: UUID) -> Path:
    dir1 = id_.hex[0:2]
    dir2 = id_.hex[2:4]
    dir3 = id_.hex[4:6]
    dir4 = id_.hex[6:8]
    rest = id_.hex[8:] + ".png"
    dir_ = temp_dir / export_id / "to" / dir1 / dir2 / dir3 / dir4
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_ / rest
