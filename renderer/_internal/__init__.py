from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from pathlib import Path

_T = TypeVar("_T")


def read_json(file: Path) -> Any:
    with file.open(encoding="utf-8") as f:
        data = json.load(f)
        f.close()
        return data


def write_json(file: Path, data: dict, pp: bool = False) -> None:
    with file.open("r+") as f:
        f.seek(0)
        f.truncate()
        if pp:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)
        f.close()


def str_to_tuple(s: str) -> tuple[int, ...]:
    return tuple([int(x) for x in s.split(", ")])


def with_next(ls: Sequence[_T]) -> Generator[tuple[_T, _T], None, None]:
    if len(ls) > 1:
        for i, a in enumerate(ls[:-1]):
            b = ls[i + 1]
            yield a, b
