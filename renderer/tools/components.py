import math
from typing import Tuple

import blessed

import renderer.internals.internal as internal  # type: ignore
import renderer.tools as tools
from renderer.objects.components import ComponentList
from renderer.objects.nodes import NodeList
from renderer.objects.skin import Skin
from renderer.types import *

term = blessed.Terminal()

def find_ends(components: ComponentList, nodes: NodeList) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
    """
    Finds the minimum and maximum X and Y values of a JSON of components
    
    :param ComponentList components: a JSON of components
    :param NodeList nodes: a JSON of nodes
    
    :returns: Returns in the form `(x_max, x_min, y_max, y_min)`
    :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
   """
    x_max = -math.inf
    x_min = math.inf
    y_max = -math.inf
    y_min = math.inf
    for component in components.component_values():
        coords = tools.nodes.to_coords(component.nodes, nodes)
        for x, y in coords:
            x_max = x if x > x_max else x_max
            x_min = x if x < x_min else x_min
            y_max = y if y > y_max else y_max
            y_min = y if y < y_min else y_min
    return x_max, x_min, y_max, y_min


def rendered_in(components: ComponentList, nodes: NodeList, min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> list[TileCoord]:
    """
    Like :py:func:`tools.line.to_tiles`, but for a JSON of components.

    :param ComponentList components: a JSON of components
    :param NodeList nodes: a JSON of nodes
    :param int min_zoom: minimum zoom value
    :param int max_zoom: maximum zoom value
    :param RealNum max_zoom_range: actual distance covered by a tile in the maximum zoom

    :returns: A list of tile coordinates
    :rtype: List[TileCoord]

    :raises ValueError: if max_zoom < min_zoom
    """
    if max_zoom < min_zoom:
        raise ValueError("Max zoom value is lesser than min zoom value")

    tiles = []
    for component in components.component_values():
        coords = tools.nodes.to_coords(component.nodes, nodes)
        tiles.extend(tools.line.to_tiles(coords, min_zoom, max_zoom, max_zoom_range))

    return tiles

 # TODO fix types
def to_geo_json(component_json: ComponentListJson, node_json: NodeListJson, skin_json: SkinJson) -> dict:
    """
    Converts component JSON into GeoJson (with nodes and skin).
   
    :param ComponentListJson component_json: a JSON of components
    :param NodeListJson node_json: a JSON of nodes
    :param SkinJson skin_json: a JSON of the skin

    :returns: A GeoJson dictionary
    :rtype: dict
    """
    ComponentList.validate_json(component_json, node_json)
    NodeList.validate_json(node_json)
    Skin.validate_json(skin_json)
    geo_json = {"type": "FeatureCollection", "features": []}

    for component_id, component in component_json.items():
        geo_feature = {"type": "Feature"}
        if not component['type'].split()[0] in skin_json['types'].keys():
            # component_type = "UNKNOWN"
            component_shape = "UNKNOWN"
            print(term.yellow(f"WARNING: Type {component['type']} not in skin file"))
        else:
            component_type = component['type'].split()[0]
            component_shape = skin_json['types'][component_type]['type']

        if component_shape == "point":
            geo_coords = list(tools.nodes.to_coords(component['nodes'], node_json)[0])
            geo_shape = "Point"
        elif component_shape == "area":
            geo_coords = [[list(c) for c in tools.nodes.to_coords(component['nodes'], node_json)]]
            if geo_coords[0][0] != geo_coords[0][-1]:
                geo_coords[0].append(geo_coords[0][0])
            if 'hollows' in component.keys():
                for hollow in component['hollows']:
                    geo_coords.append([list(c) for c in tools.nodes.to_coords(hollow, node_json)])
                    if geo_coords[-1][0] != geo_coords[-1][-1]:
                        geo_coords[-1].append(geo_coords[-1][0])
            geo_shape = "Polygon"
        else:
            geo_coords = [list(c) for c in tools.nodes.to_coords(component['nodes'], node_json)]
            geo_shape = "LineString"
        geo_feature['geometry'] = {
            "type": geo_shape,
            "coordinates": geo_coords
        }

        geo_feature['properties'] = {
            "name": component_id,
            "component_type": component['type'],
            "displayname": component['displayname'],
            "description": component['description'],
            "layer": component['layer']
        }
        for k, v in component['attrs'].items():
            geo_feature['properties'][k] = v

        geo_json['features'].append(geo_feature)

    return geo_json