import blessed

import renderer.internals.internal as internal
import renderer.validate as validate
from renderer.types import *

term = blessed.Terminal()

def to_component_node_json(geo_json: dict) -> Tuple[ComponentJson, NodeJson]:
    """
    Converts GeoJson to component and node JSONs.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.geoJson.toNodePlaJson
    """
    validate.v_geo_json(geo_json)
    component_json = {}
    node_json = {}

    def add_node(x, y):
        for k, v in node_json.items():
            if v['x'] == x and v['y'] == y:
                return k
        k = internal.genId()
        node_json[k] = {
            "x": x,
            "y": y,
            "connections": []
        }
        return k

    def single_geometry(geo, properties, name=None):
        if name is None:
            if 'name' in properties.keys():
                name = properties['name']
            else:
                name = internal.genId()
        component_type = properties['component_type'] if "component_type" in properties else "UNKNOWN"
        displayname = properties['displayname'] if "displayname" in properties else ""
        description = properties['description'] if "description" in properties else ""
        layer = properties['layer'] if "layer" in properties else 0
        attrs = {}
        for k, v in properties.items():
            if k not in ['name', 'component_type', 'displayname', 'description', 'layer']:
                attrs[k] = v

        hollows = []
        if geo['type'] == "Polygon":
            nodes = [add_node(*c) for c in geo['coordinates'][0]]
            if len(geo['coordinates']) > 1:
                for i in range(1, len(geo['coordinates'])):
                    hollows.append([add_node(*c) for c in geo['coordinates'][i]])
        elif geo['type'] == "LineString":
            nodes = [add_node(*c) for c in geo['coordinates']]
        else:
            nodes = add_node(*geo['coordinates'])
        component_json[name] = {
            "type": component_type,
            "displayname": displayname,
            "description": description,
            "layer": layer,
            "nodes": nodes,
            "attrs": attrs
        }
        if hollows: component_json[name]['hollows'] = hollows

    def single_feature(feature: dict):
        name = feature['properties']['name'] if 'name' in feature['properties'].keys() else internal.genId()
        if feature['geometry']['type'] == "GeometryCollection":
            for itemNo, sub_geo in enumerate(feature['geometry']['geometries']):
                single_geometry(sub_geo, feature['properties'], name=name + "_" + itemNo)
        elif feature['geometry']['type'].startswith("Multi"):
            for sub_coord in feature['geometry']['coordinates']:
                single_geometry({"type": feature['geometry']['type'].replace("Multi", ""), "coordinates": sub_coord},
                                feature['properties'], name=name)
        else:
            single_geometry(feature['geometry'], feature['properties'])

    for feature in geo_json['features']:
        single_feature(feature)
    return component_json, node_json