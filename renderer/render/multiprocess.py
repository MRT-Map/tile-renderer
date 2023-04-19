from __future__ import annotations

import functools
import logging
import traceback
from dataclasses import dataclass
from queue import Empty, Queue
from typing import TYPE_CHECKING, Generic, TypeVar

import psutil
import ray
from rich.progress import Progress, track
from rich.traceback import install

if TYPE_CHECKING:
    from collections.abc import Callable
    from ray.types import ObjectRef

from .._internal.logger import log

_I = TypeVar("_I")
_D = TypeVar("_D")
_R = TypeVar("_R")


@ray.remote
class ProgressHandler(Generic[_I]):
    """The handler for progress bars"""

    def __init__(self) -> None:
        self.queue: Queue[_I] = Queue()
        """The queue of TileCoords to be processed"""
        self.completed: Queue[_I] = Queue()
        """The list of completed TileCoords"""
        self.new_tasks_needed: Queue[None] = Queue()
        """If this queue has something, a new task is needed"""

    def add(self, id_: _I) -> None:
        """Add a TileCoord to the queue"""
        self.queue.put_nowait(id_)

    def get(self) -> _I | None:
        """Get the first TileCoord in the queue"""
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def _complete(self, id_: _I) -> None:
        """Complete a TileCoord"""
        self.completed.put_nowait(id_)

    def get_complete(self) -> _I | None:
        """Get the first completed TileCoord in the queue"""
        try:
            return self.completed.get_nowait()
        except Empty:
            return None

    def request_new_task(self) -> None:
        """Request a new task to be processed"""
        self.new_tasks_needed.put_nowait(None)

    def needs_new_task(self) -> bool:
        """Returns True if a new task is needed, and resets the value to False"""
        try:
            self.queue.get_nowait()
        except Empty:
            return False
        else:
            return True


@ray.remote
def task_spawner(
    ph: ObjectRef[ProgressHandler[_I]],
    chunks: list[list[_I]],
    const_data: _D,
    f: Callable[[ObjectRef[ProgressHandler[_I]] | None, list[_I], _D], list[_R] | None],
    futures: list[ObjectRef[list[_R] | None]],
    cursor: int,
) -> list[ObjectRef[list[_R] | None]]:
    """The task spawner used for part 1"""
    while cursor < len(chunks):
        if ray.get(ph.needs_new_task.remote()):
            output: ObjectRef[list[_R] | None]
            output = ray.remote(f).remote(ph, chunks[cursor], const_data)
            futures.append(output)
            cursor += 1
    return futures


@dataclass(frozen=True, init=True, unsafe_hash=True)
class MultiprocessConfig:
    batch_size: int = psutil.cpu_count()
    chunk_size: int = 8
    serial: bool = False


def multiprocess(
    iterated: list[_I],
    const_data: _D,
    f: Callable[[ObjectRef[ProgressHandler[_I]] | None, _I, _D], _R | None],
    msg: str,
    num_operations: int | None = None,
    mp_config: MultiprocessConfig = MultiprocessConfig(),  # noqa: B008
) -> list[_R]:
    if mp_config.serial:
        out_ = []
        for i_ in track(iterated, msg):
            o_ = f(None, i_, const_data)
            if o_ is not None:
                out_.append(o_)
        return out_

    const_data = ray.put(const_data)

    chunks = [
        iterated[i : i + mp_config.chunk_size]
        for i in range(0, len(iterated), mp_config.chunk_size)
    ]

    @functools.wraps(f)
    def new_f(
        p: ObjectRef[ProgressHandler[_I]] | None,
        i: list[_I],
        d: _D,
    ) -> list[_R] | None:
        install(show_locals=True)
        logging.getLogger("fontTools").setLevel(logging.CRITICAL)
        logging.getLogger("PIL").setLevel(logging.CRITICAL)
        out = []
        for j in i:
            try:
                o = f(p, j, d)
                if o is not None:
                    out.append(o)
            except Exception as e:  # noqa: BLE001
                log.error(f"Error in ray task: {e!r}")
                log.error(traceback.format_exc())
            if p:
                p._complete.remote(j)
        if p:
            p.request_new_task.remote()

        return out

    ph = ProgressHandler.remote()

    futures: list[ObjectRef[_R]]
    futures = [
        ray.remote(new_f).remote(ph, chunk, const_data)
        for chunk in track(
            chunks[: mp_config.batch_size], "Spawning initial tasks", transient=True
        )
    ]
    cursor = mp_config.batch_size
    future_refs: ObjectRef[list[ObjectRef[list[_R] | None]]]
    future_refs = task_spawner.remote(ph, chunks, const_data, new_f, futures, cursor)
    with Progress() as progress:
        main_id = progress.add_task(msg, total=num_operations)
        num_complete = 0
        while num_complete < len(iterated):
            id_: _I | None = ray.get(ph.get_complete.remote())
            if id_ is not None:
                num_complete += 1
            id2: _I | None = ray.get(ph.get.remote())
            if id2 is not None:
                progress.advance(main_id, 1)
        progress.update(main_id, completed=num_operations)

    pre_result: list[ObjectRef[list[_R] | None]]
    pre_result = ray.get(future_refs)
    result: list[_R] = [b for a in ray.get(pre_result) if a is not None for b in a]
    return result
