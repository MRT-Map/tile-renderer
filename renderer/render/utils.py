from __future__ import annotations

from queue import Empty, Queue

import ray

from renderer.types.coord import TileCoord


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
