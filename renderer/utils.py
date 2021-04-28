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

import renderer.internal
import renderer.tools
import renderer.mathtools
init()

def coordListIntegrity(coords: list):
    for item in coords:
        if not isinstance(item, tuple):
            raise TypeError(f"Coordinates {item} is not type 'tuple'")
        elif len(item) != 2:
            raise ValueError(f"Coordinates {item} has {len(item)} values instead of 2")
        for n in item:
            if not isinstance(n, (int, float)):
                raise TypeError(f"Coordinate {n} is not type 'int/float'")
    return True

def tileCoordListIntegrity(tiles: list, minZoom: int, maxZoom: int):
    for item in tiles:
        if not isinstance(item, tuple):
            raise TypeError(f"Tile coordinates {item} is not type 'tuple'")
        elif len(item) != 3:
            raise ValueError(f"Tile coordinates {item} has {len(item)} values instead of 3")
        for n in item:
            if not isinstance(n, (int, float)):
                raise TypeError(f"Tile coordinate {n} is not type 'int/float'")
        if not minZoom <= item[0] <= maxZoom:
            raise ValueError(f"Zoom value {item[0]} is not in the range {minZoom} <= z <= {maxZoom}")
        elif not isinstance(item[0], int):
            raise TypeError(f"Zoom value {item[0]} is not an integer")
    return True

def nodeListIntegrity(nodes: list, nodeList: dict):
    for node in nodes:
        if not node in nodeList.keys():
            raise ValueError(f"Node '{node}' does not exist")

    return True

def nodeJsonIntegrity(nodeList: dict):
    schema = Schema({
        str: {
            "x": Or(int, float),
            "y": Or(int, float),
            "connections": list
        }
    })
    schema.validate(nodeList)
    return True

def plaJsonIntegrity(plaList: dict, nodeList: dict):
    schema = Schema({
        str: {
            "type": str,
            "displayname": str,
            "description": str,
            "layer": Or(int, float),
            "nodes": And(list, lambda i: nodeListIntegrity(i, nodeList)),
            "attrs": dict
        }
    })
    schema.validate(plaList)
    return True
            
def skinJsonIntegrity(skinJson: dict):
    mainSchema = Schema({
        "info": {
            "size": int,
            "font": {
                "": str,
                "b": str,
                "i": str,
                "bi": str
            },
            "background": And([int], lambda l: len(l) == 3 and not False in [0 <= n <= 255 for n in l])
        },
        "order": [str],
        "types": {
            str: {
                "tags": list,
                "type": lambda s: s in ['point', 'line', 'area'],
                "style": {
                    str: list
                }
            }
        }
    })
    point_circle = Schema({
        "layer": "circle",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "size": int,
        "width": int
    })
    point_text = Schema({
        "layer": "text",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "offset": And([int], lambda o: len(o) == 2),
        "size": int,
        "anchor": Or(None, str)
    })
    point_square = Schema({
        "layer": "square",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "size": int,
        "width": int
    })
    point_image = Schema({
        "layer": "image",
        "file": str,
        "offset": And([int], lambda o: len(o) == 2)
    })
    line_backfore = Schema({
        "layer": Or("back", "fore"),
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "width": int,
        Optional("dash"): And([int], lambda l: len(l) == 2)
    })
    line_text = Schema({
        "layer": "text",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "size": int,
        "offset": int
    })
    area_fill = Schema({
        "layer": "fill",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        Optional("stripe"): And([int], lambda l: len(l) == 3)
    })
    area_bordertext = Schema({
        "layer": "bordertext",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "offset": int,
        "size": int
    })
    area_centertext = Schema({
        "layer": "centertext",
        "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
        "size": int,
        "offset": And(And(list, [int]), lambda o: len(o) == 2)
    })
    area_centerimage = Schema({
        "layer": "image",
        "file": str,
        "offset": And(And(list, [int]), lambda o: len(o) == 2)
    })

    schemas = {
        "point": {
            "circle": point_circle,
            "text": point_text,
            "square": point_square,
            "image": point_image
        },
        "line": {
            "text": line_text,
            "back": line_backfore,
            "fore": line_backfore
        },
        "area": {
            "bordertext": area_bordertext,
            "centertext": area_centertext,
            "fill": area_fill,
            "centerimage": area_centerimage
        }
    }

    mainSchema.validate(skinJson)
    for n, t in skinJson['types'].items():
        if not n in skinJson['order']:
            raise ValueError(f"Type {n} is not in order list")
        s = t['style']
        for z, steps in s.items():
            if internal.strToTuple(z)[0] > internal.strToTuple(z)[1]:
                raise ValueError(f"Invalid range '{z}'")
            for step in steps:
                if not step["layer"] in schemas[t['type']]:
                    raise ValueError(f"Invalid layer '{step}'")
                else:
                    try:
                        schemas[t['type']][step['layer']].validate(step)
                    except Exception as e:
                        print(Fore.RED + f"Type {n}, range {z}, step {step['layer']}" + Style.RESET_ALL)
                        raise e