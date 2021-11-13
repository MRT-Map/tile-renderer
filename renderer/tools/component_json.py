import math
import blessed

import renderer.internals.internal as internal # type: ignore
import renderer.validate as validate
import renderer.tools as tools
from renderer.types import *

term = blessed.Terminal()

def find_ends(component_json: ComponentJson, node_json: NodeJson) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
    """
    Finds the minimum and maximum X and Y values of a JSON or dictionary of components
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.plaJson.findEnds
    """
    validate.v_component_json(component_json, node_json)
    validate.v_node_json(node_json)
    x_max = -math.inf
    x_min = math.inf
    y_max = -math.inf
    y_min = math.inf
    for component in component_json.keys():
        coords = tools.nodes.to_coords(component_json[component]['nodes'], node_json)
        for x, y in coords:
            x_max = x if x > x_max else x_max
            x_min = x if x < x_min else x_min
            y_max = y if y > y_max else y_max
            y_min = y if y < y_min else y_min
    return x_max, x_min, y_max, y_min


def rendered_in(component_json: ComponentJson, node_json: NodeJson, min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> List[TileCoord]:
    """
    Like renderer.tools.lineToTiles(), but for a JSON or dictionary of components.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.plaJson.renderedIn
    """
    validate.v_component_json(component_json, node_json)
    validate.v_node_json(node_json)
    if max_zoom < min_zoom:
        raise ValueError("Max zoom value is lesser than min zoom value")

    tiles = []
    for component in component_json.keys():
        coords = tools.nodes.to_coords(component_json[component]['nodes'], node_json)
        tiles.extend(tools.line.to_tiles(coords, min_zoom, max_zoom, max_zoom_range))

    return tiles


def to_geo_json(component_json: ComponentJson, node_json: NodeJson, skin_json: SkinJson) -> dict:
    """
    Converts component Json into GeoJson (with nodes and skin).
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.plaJson.toGeoJson
    """
    validate.v_component_json(component_json, node_json)
    validate.v_node_json(node_json)
    validate.v_skin_json(skin_json)
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