import blessed
from schema import Schema, And, Or, Regex, Optional
from typing import Union, List, Tuple

import renderer.internals.internal as internal # type: ignore
import renderer.tools as tools
import renderer.mathtools as mathtools
import renderer.misc as misc

RealNum = Union[int, float]
Coord = Tuple[RealNum, RealNum]
TileCoord = Tuple[int, int, int]

def v_coords(coords: List[Coord]) -> True:
    """
    Validates a list of coordinates.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.validate.coords
    """
    for item in coords:
        if not isinstance(item, (tuple, list)):
            raise TypeError(f"Coordinates {item} is not type 'tuple'")
        elif len(item) != 2:
            raise ValueError(f"Coordinates {item} has {len(item)} values instead of 2")
        for n in item:
            if not isinstance(n, (int, float)):
                raise TypeError(f"Coordinate {n} is not type 'int/float'")
    return True

def v_tile_coords(tiles: List[TileCoord], min_zoom: int, max_zoom: int) -> True:
    """
    Validates a list of tile coordinates.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.validate.tileCoords
    """
    for item in tiles:
        if not isinstance(item, tuple):
            raise TypeError(f"Tile coordinates {item} is not type 'tuple'")
        elif len(item) != 3:
            raise ValueError(f"Tile coordinates {item} has {len(item)} values instead of 3")
        for n in item:
            if not isinstance(n, (int, float)):
                raise TypeError(f"Tile coordinate {n} is not type 'int/float'")
        if not min_zoom <= item[0] <= max_zoom:
            raise ValueError(f"Zoom value {item[0]} is not in the range {min_zoom} <= z <= {max_zoom}")
        elif not isinstance(item[0], int):
            raise TypeError(f"Zoom value {item[0]} is not an integer")
    return True

def v_node_list(nodes: List[str], node_list: dict) -> True:
    """
    Validates a list of node IDs.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.validate.nodeList
    """
    for node in nodes:
        if node not in node_list.keys():
            raise ValueError(f"Node '{node}' does not exist")

    return True

def v_node_json(node_json: dict) -> True:
    """
    Validates a dictionary/JSON of nodes.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.validate.nodeJson
    """
    schema = Schema({
        str: {
            "x": Or(int, float),
            "y": Or(int, float),
            "connections": list
        }
    })
    schema.validate(node_json)
    return True

def v_component_json(component_json: dict, node_json: dict) -> True:
    """
    Validates a dictionary/JSON of components.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.validate.plaJson
    """
    schema = Schema({
        str: {
            "type": str,
            "displayname": str,
            "description": str,
            "layer": Or(int, float),
            "nodes": And(list, lambda i: v_node_list(i, node_json)),
            Optional("hollows"): [And(list, lambda i: v_node_list(i, node_json))],
            "attrs": dict
        }
    })
    schema.validate(component_json)
    return True
            
def v_skin_json(skin_json: dict) -> True:
    """
    Validates a skin JSON file.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.validate.skinJson
    """
    mainSchema = Schema({
        "info": {
            "size": int,
            "font": {
                "": str,
                "b": str,
                "i": str,
                "bi": str
            },
            "background": And([int], lambda l: len(l) == 3 and False not in [0 <= n_ <= 255 for n_ in l])
        },
        "order": [str],
        "types": {
            str: {
                "tags": list,
                "type": lambda t_: t_ in ['point', 'line', 'area'],
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

    mainSchema.validate(skin_json)
    for n, t in skin_json['types'].items():
        if n not in skin_json['order']:
            raise ValueError(f"Type {n} is not in order list")
        s = t['style']
        for z, steps in s.items():
            if internal._str_to_tuple(z)[0] > internal._str_to_tuple(z)[1]:
                raise ValueError(f"Invalid range '{z}'")
            for step in steps:
                if not step["layer"] in schemas[t['type']]:
                    raise ValueError(f"Invalid layer '{step}'")
                else:
                    try:
                        schemas[t['type']][step['layer']].validate(step)
                    except Exception as e:
                        term = blessed.Terminal()
                        print(term.red(f"Type {n}, range {z}, step {step['layer']}"))
                        raise e

def v_geo_json(geo_json: dict) -> True:
    mainSchema = Schema({
        "type": "FeatureCollection", 
        "features": [{
            "type": "Feature",
            "geometry": dict,
            "properties": dict
        }]
    }, ignore_extra_keys=True)

    point = Schema({
        "type": "Point",
        "coordinates": And([int, float], lambda c: len(c) == 2)
    }, ignore_extra_keys=True)

    lineString = Schema({
        "type": "LineString",
        "coordinates": v_coords
    }, ignore_extra_keys=True)

    polygon = Schema({
        "type": "Polygon",
        "coordinates": lambda cs: all([v_coords(c) and c[0] == c[-1] for c in cs])
    }, ignore_extra_keys=True)

    multiPoint = Schema({
        "type": "MultiPoint",
        "coordinates": v_coords
    }, ignore_extra_keys=True)

    multiLineString = Schema({
        "type": "MultiLineString",
        "coordinates": lambda cs: all([v_coords(c) for c in cs])
    }, ignore_extra_keys=True)

    multiPolygon = Schema({
        "type": "MultiPolygon",
        "coordinates": lambda css: all([all([v_coords(c) and c[0] == c[-1] for c in cs]) for cs in css])
    }, ignore_extra_keys=True)

    def vGeometry(geo: dict):
        schemas = {
            "Point": point,
            "LineString": lineString,
            "Polygon": polygon,
            "MultiPoint": multiPoint,
            "MultiLineString": multiLineString,
            "MultiPolygon": multiPolygon
        }

        if geo['type'] == "GeometryCollection":
            for sub_geo in geo['geometries']:
                vGeometry(sub_geo)
        elif geo['type'] in schemas.keys():
            schemas[geo['type']].validate(geo)
        else:
            raise ValueError(f"Invalid type {geo['type']}")

    mainSchema.validate(geo_json)
    for feature in geo_json['features']:
        vGeometry(feature['geometry'])

    return True