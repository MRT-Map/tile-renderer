import math
import blessed
from typing import Union, List, Dict, Tuple
term = blessed.Terminal()

import renderer.internals.internal as internal # type: ignore
import renderer.validate as validate
import renderer.mathtools as mathtools
import renderer.misc as misc

RealNum = Union[int, float]
Coord = Tuple[RealNum, RealNum]
TileCoord = Tuple[int, int, int]

class component_json:
    @staticmethod
    def find_ends(component_json: dict, node_json: dict) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
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
            coords = nodes.to_coords(component_json[component]['nodes'], node_json)
            for x, y in coords:
                x_max = x if x > x_max else x_max
                x_min = x if x < x_min else x_min
                y_max = y if y > y_max else y_max
                y_min = y if y < y_min else y_min
        return x_max, x_min, y_max, y_min

    @staticmethod
    def rendered_in(component_json: dict, node_json: dict, min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> List[TileCoord]:
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
            coords = nodes.to_coords(component_json[component]['nodes'], node_json)
            tiles.extend(line.to_tiles(coords, min_zoom, max_zoom, max_zoom_range))

        return tiles

    @staticmethod
    def to_geo_json(component_json: dict, node_json: dict, skin_json: dict) -> dict:
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
                component_type = "UNKNOWN"
                component_shape = "UNKNOWN"
                print(term.yellow(f"WARNING: Type {component['type']} not in skin file"))
            else:
                component_type = component['type'].split()[0]
                component_shape = skin_json['types'][component_type]['type']
            
            if component_shape == "point":
                geo_coords = list(nodes.to_coords(component['nodes'], node_json)[0])
                geo_shape = "Point"
            elif component_shape == "area":
                geo_coords = [[list(c) for c in nodes.to_coords(component['nodes'], node_json)]]
                if geo_coords[0][0] != geo_coords[0][-1]:
                    geo_coords[0].append(geo_coords[0][0])
                if 'hollows' in component.keys():
                    for hollow in component['hollows']:
                        geo_coords.append([list(c) for c in nodes.to_coords(hollow, node_json)])
                        if geo_coords[-1][0] != geo_coords[-1][-1]:
                            geo_coords[-1].append(geo_coords[-1][0])
                geo_shape = "Polygon"
            else:
                geo_coords = [list(c) for c in nodes.to_coords(component['nodes'], node_json)]
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

class geo_json:
    @staticmethod
    def to_component_node_json(geo_json: dict) -> Tuple[dict, dict]:
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
                if 'name' in properties.keys(): name = properties['name']
                else: name = internal.genId()
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
                    single_geometry(sub_geo, feature['properties'], name=name+"_"+itemNo)
            elif feature['geometry']['type'].startswith("Multi"):
                for sub_coord in feature['geometry']['coordinates']:
                    single_geometry({"type": feature['geometry']['type'].replace("Multi", ""), "coordinates": sub_coord}, feature['properties'], name=name)
            else:
                single_geometry(feature['geometry'], feature['properties'])

        for feature in geo_json['features']:
            single_feature(feature)
        return component_json, node_json
            
class tile:
    @staticmethod
    def find_ends(coords: List[TileCoord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
        """
        Find the minimum and maximum x/y values of a set of tiles coords.
        More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.tile.findEnds
        """
        validate.v_tile_coords(coords, -math.inf, math.inf)
        x_max = -math.inf
        x_min = math.inf
        y_max = -math.inf
        y_min = math.inf
        for _, x, y in coords:
            x_max = x if x > x_max else x_max
            x_min = x if x < x_min else x_min
            y_max = y if y > y_max else y_max
            y_min = y if y < y_min else y_min
        return x_max, x_min, y_max, y_min

class line:
    @staticmethod
    def find_ends(coords: List[Coord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]:
        """
        Find the minimum and maximum x/y values of a set of coords.
        More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.line.findEnds
        """
        validate.v_coords(coords)
        x_max = -math.inf
        x_min = math.inf
        y_max = -math.inf
        y_min = math.inf
        for x, y in coords:
            x_max = x if x > x_max else x_max
            x_min = x if x < x_min else x_min
            y_max = y if y > y_max else y_max
            y_min = y if y < y_min else y_min
        return x_max, x_min, y_max, y_min

    @staticmethod
    def to_tiles(coords: List[Coord], min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> List[TileCoord]:
        """
        Generates tile coordinates from list of regular coordinates using renderer.tools.coordToTiles().
        More info: Mainly for rendering whole components. https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.line.toTiles
        """
        validate.v_coords(coords)
        if len(coords) == 0:
            raise ValueError("Empty list of coords given")
        elif max_zoom < min_zoom:
            raise ValueError("Max zoom value is lesser than min zoom value")
        
        tiles = []
        x_max = -math.inf
        x_min = math.inf
        y_max = -math.inf
        y_min = math.inf
        
        for x, y in coords:
            x_max = x+10 if x > x_max else x_max
            x_min = x-10 if x < x_min else x_min
            y_max = y+10 if y > y_max else y_max
            y_min = y-10 if y < y_min else y_min
        xr = list(range(x_min, x_max + 1, int(max_zoom_range / 2)))
        xr.append(x_max+1)
        yr = list(range(y_min, y_max + 1, int(max_zoom_range / 2)))
        yr.append(y_max+1)
        for x in xr:
            for y in yr:
                tiles.extend(coord.to_tiles((x, y), min_zoom, max_zoom, max_zoom_range))
        tiles = list(dict.fromkeys(tiles))
        return tiles

class nodes:
    @staticmethod
    def find_components_attached(node_id: str, component_json: dict) -> List[Tuple[str, int]]:
        """
        Finds which components attach to a node.
        More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.nodes.findPLAsAttached
        """
        components = []
        for component_id, component in component_json.items():
            #print(component_id)
            if node_id in component['nodes']:
                components.append((component_id, component['nodes'].index(node_id)))
        return components

    @staticmethod
    def to_coords(nodes: List[str], node_json: dict) -> List[Coord]:
        """
        Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.
        More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.nodes.toCoords
        """
        validate.v_node_json(node_json)
        validate.v_node_list(nodes, node_json)
        coords = []
        for node_id in nodes:
            if node_id not in node_json.keys():
                raise KeyError(f"Node '{node_id}' does not exist")
            coords.append((node_json[node_id]['x'], node_json[node_id]['y']))
        return coords

class coord:
    @staticmethod
    def to_tiles(coord: Coord, min_zoom: int, max_zoom: int, max_zoom_range: RealNum) -> List[TileCoord]:
        """
        Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.
        More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.tools.coord.toTiles
        """
        if max_zoom < min_zoom:
            raise ValueError("Max zoom value is lesser than min zoom value")

        tiles = []
        for z in reversed(range(min_zoom, max_zoom + 1)):
            x = math.floor(coord[0] / max_zoom_range)
            y = math.floor(coord[1] / max_zoom_range)
            tiles.append((z,x,y))
            max_zoom_range *= 2

        return tiles