import math
import json
from typing import Union
import time
import random

def dictIndex(d: dict, v):
    return list(d.keys())[list(d.values()).index(v)]

def readJson(file: str):
    with open(file, "r") as f:
        data = json.load(f)
        f.close()
        return data

def writeJson(file: str, data: dict, pp=False):
    with open(file, "r+") as f:
        f.seek(0)
        f.truncate()
        if pp:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)
        f.close()

def tupleToStr(t: tuple):
    return str(t)[1:-1]

def strToTuple(s: str):
    return tuple([int(x) for x in s.split(", ")])

def msToTime(ms: Union[int, float]):
    if ms == 0:
        return "00.0s"
    s = round(ms / 1000, 1)
    #ms = round(ms % 1000, 2)
    m = math.floor(s / 60)
    s = s % 60
    h = math.floor(m / 60)
    m = m % 60
    d = math.floor(h / 24)
    h = h % 24
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
    #if ms != 0:
    #    pzero = "00" if ms < 10 else "0" if 10 <= ms < 100 else ""
    #    szero = "0" if len(str(ms).split(".")[1]) == 1 else ""
    #    res = res + pzero + str(ms) + szero + "ms "
    return res.strip()

def percentage(c: Union[int, float], t: Union[int, float]):
    res = round(c/t*100, 2)
    pzero = "0" if res < 10 else ""
    szero = "0" if len(str(res).split(".")[1]) == 1 else ""
    return pzero + str(res) + szero

def timeRemaining(start: Union[int, float], c: Union[int, float], t: Union[int, float]):
    return round(((int(round(time.time() * 1000)) - start) / c * (t - c)), 2)

def genId():
    def b10_b64(n: int):
        BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        q = n
        o = ""
        while True:
            o += BASE64[q % 64]
            q = math.floor(q / 64)
            if q == 0:
                break
        return o[::-1]
    decimalId = int(time.time() * 10000000)
    return b10_b64(decimalId) + "-" + b10_b64(random.randint(1, 64**5))