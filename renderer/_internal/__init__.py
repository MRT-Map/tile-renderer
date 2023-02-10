from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generator, Sequence, TypeVar

_T = TypeVar("_T")


def read_json(file: Path | str) -> Any:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        f.close()
        return data


def write_json(file: Path | str, data: dict, pp: bool = False):
    with open(file, "r+") as f:
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
