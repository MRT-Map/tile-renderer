from schema import Schema, And

from renderer.objects.nodes import NodeList
from renderer.types import *
from schema import Schema, And

from renderer.objects.nodes import NodeList
from renderer.types import *


def v_coords(coords: List[Coord]) -> Literal[True]:
    """
    Validates a list of coordinates.
      
    :param List[Coord] coords: a list of coordinates.
        
    :returns: Returns True if no errors
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

def v_tile_coords(tiles: List[TileCoord], min_zoom: int, max_zoom: int) -> Literal[True]:
    """
    Validates a list of tile coordinates.
      
    :param List[TileCoord] tiles: a list of tile coordinates.
    :param int min_zoom: minimum zoom value
    :param int max_zoom: maximum zoom value
        
    :returns: Returns True if no errors
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

def v_node_list(nodes: List[str], all_nodes: NodeList) -> Literal[True]:
    """
    Validates a list of node IDs.
      
    :param List[str] nodes: a list of node IDs.
    :param NodeList all_nodes: a dictionary of nodes
        
    :returns: Returns True if no errors
    """
    for node in nodes:
        if node not in all_nodes.node_ids():
            raise ValueError(f"Node '{node}' does not exist")

    return True

def v_geo_json(geo_json: dict) -> Literal[True]:
    """
    Validates a GeoJson file.

    :param dict geo_json: the GeoJson file
    
    :returns: Returns True if no errors
    """
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