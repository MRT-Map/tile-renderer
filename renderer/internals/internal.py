from __future__ import annotations

import math
import json
from pathlib import Path
from typing import TypeVar, Any, Generator, Sequence
import time
import random
import blessed
import difflib
import re

term = blessed.Terminal()


def _dedent(text: str) -> str:
    return re.sub("\n ", "\n", re.sub(" +", " ", text))


_K = TypeVar("_K")
_V = TypeVar("_V")


def _dict_index(d: dict[_K, _V], v: _V) -> _K:
    return list(d.keys())[list(d.values()).index(v)]


def _read_json(file: Path | str) -> Any:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        f.close()
        return data


def _write_json(file: Path | str, data: dict, pp: bool = False):
    with open(file, "r+") as f:
        f.seek(0)
        f.truncate()
        if pp:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)
        f.close()


def _tuple_to_str(t: tuple) -> str:
    return str(t)[1:-1]


def _str_to_tuple(s: str) -> tuple:
    return tuple([int(x) for x in s.split(", ")])


def _ms_to_time(ms: int | float) -> str:
    if ms == 0:
        return "00.0s"
    s = round(ms / 1000, 1)
    # ms = round(ms % 1000, 2)
    m = math.floor(s / 60)
    s %= 60
    h = math.floor(m / 60)
    m %= 60
    d = math.floor(h / 24)
    h %= 24
    res = ""
    if d != 0:
        res = res + str(d) + "d "
    if h != 0:
        zero = "0" if h < 10 else ""
        res = res + zero + str(h) + "h "
    if m != 0:
        zero = "0" if m < 10 else ""
        res = res + zero + str(m) + "min "
    if s != 0:
        zero = "0" if s < 10 else ""
        res = res + zero + str(round(s, 1)) + "s "
    if res == "":
        res = "00.0s"
    return res.strip()


def _percentage(c: int | float, t: int | float) -> str:
    res = round(c / t * 100, 2)
    pzero = "0" if res < 10 else ""
    szero = "0" if len(str(res).split(".")[1]) == 1 else ""
    return pzero + str(res) + szero


def _time_remaining(start: int | float, c: int | float, t: int | float) -> float:
    return round(((int(round(time.time() * 1000)) - start) / c * (t - c)), 2)


def _gen_id() -> str:
    def b10_b64(n: int):
        base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        q = n
        o = ""
        while True:
            o += base64[q % 64]
            q = math.floor(q / 64)
            if q == 0:
                break
        return o[::-1]

    decimal_id = int(time.time() * 10000000)
    return b10_b64(decimal_id) + "-" + b10_b64(random.randint(1, 64**5))


def _ask_file_name(name: str) -> tuple[dict, str]:
    file_confirmed = False
    file_path = ""
    while not file_confirmed:
        file_path = input(
            term.yellow(f"Which {name} JSON file are you writing to/referencing? ")
        )
        try:
            open(file_path, "r")
            if file_path.endswith(".json"):
                file_confirmed = True
            else:
                print(term.red("File is not a JSON file"))
        except FileNotFoundError:
            print(term.red("File does not exist"))

    with open(file_path, "r") as f:
        data = json.load(f)
        f.close()

    return data, file_path


_T = TypeVar("_T")


def _similar(s: _T, i: list[_T]):
    if len(sim := difflib.get_close_matches(s, i)) != 0:
        print(term.bright_red(f"Perhaps you mean: {', '.join(sim)}"))


def _with_next(ls: Sequence[_T]) -> Generator[tuple[_T, _T], None, None]:
    if len(ls) > 1:
        for i, a in enumerate(ls[:-1]):
            b = ls[i + 1]
            yield a, b
