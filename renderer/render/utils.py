from __future__ import annotations

from queue import Queue

import ray

from renderer.types.coord import TileCoord


@ray.remote
class ProgressHandler:
    def __init__(self):
        self.queue = Queue()
        self.completed = 0

    def add(self, id_: TileCoord):
        self.queue.put_nowait(id_)

    def get(self) -> TileCoord:
        return self.queue.get_nowait()

    def complete(self):
        self.completed += 1

    def get_complete(self):
        return self.completed
