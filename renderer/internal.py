from colorama import Fore, Style, init
import math
import json
from PIL import Image, ImageDraw, ImageFont
import sympy as sym
from typing import Union
import time
import glob
import re
import numpy as np
from schema import Schema, And, Or, Regex, Optional
import multiprocessing
import tqdm
import sys
init()

def log(msg: str, pLevel: int, vLevel: int, logPrefix=""):
    colour = {
        "0": Fore.GREEN,
        "1": "",
        "2": Style.DIM
    }
    if pLevel <= vLevel:
        print(colour[str(pLevel)] + logPrefix + msg + Style.RESET_ALL)

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
        return "0ms"
    s = math.floor(ms / 1000)
    ms = round(ms % 1000, 2)
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
        res = res + str(h) + "h "
    if m != 0:
        res = res + str(m) + "min "
    if s != 0:
        res = res + str(s) + "s "
    if ms != 0:
        res = res + str(ms) + "ms "
    return res.strip()