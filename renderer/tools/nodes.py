import blessed

import renderer.internals.internal as internal # type: ignore
import renderer.validate as validate
from renderer.old_types import *

term = blessed.Terminal()

def find_components_attached(node_id: str, component_json: ComponentJson) -> List[Tuple[str, int]]:
    """
    Finds which components attach to a node.
   
    :param str node_id: the node to search for
    :param ComponentJson component_json: a JSON of components
    
    :returns: A list of tuples in the form of ``(component_id, index)``
    :rtype: List[Tuple[str, int]]
    """
    components = []
    for component_id, component in component_json.items():
        #print(component_id)
        if node_id in component['nodes']:
            components.append((component_id, component['nodes'].index(node_id)))
    return components

def to_coords(nodes: List[str], node_json: NodeJson) -> List[Coord]:
    """
    Converts a list of nodes IDs into a list of coordinates with a JSON of nodes as its reference.
   
   :param List[str] nodes: a list of node IDs
   :param NodeJson node_json: a JSON of nodes
   
   :returns: A list of coordinates
   :rtype: List[Coord]

   :raises KeyError: if a node does not exist"""
    validate.v_node_json(node_json)
    validate.v_node_list(nodes, node_json)
    coords = []
    for node_id in nodes:
        if node_id not in node_json.keys():
            raise KeyError(f"Node '{node_id}' does not exist")
        coords.append((node_json[node_id]['x'], node_json[node_id]['y']))
    return coords