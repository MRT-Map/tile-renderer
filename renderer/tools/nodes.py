from typing import Tuple, List

import blessed

import renderer.internals.internal as internal  # type: ignore
from renderer.objects.components import ComponentList, Component
from renderer.objects.nodes import NodeList
from renderer.types import Coord

term = blessed.Terminal()

def find_components_attached(node_id: str, components: ComponentList) -> List[Tuple[Component, int]]:
    """
    Finds which components attach to a node.
   
    :param str node_id: the node to search for
    :param ComponentList components: a list of components
    
    :returns: A list of tuples in the form of ``(component_id, index)``
    :rtype: List[Tuple[str, int]]
    """
    attached_components = []
    for component in components.component_values():
        #print(component_id)
        if node_id in component.nodes:
            attached_components.append((component, component.nodes.index(node_id)))
    return attached_components

def to_coords(nodes: List[str], node_list: NodeList) -> List[Coord]:
    """
    Converts a list of nodes IDs into a list of coordinates with a JSON of nodes as its reference.
   
   :param List[str] nodes: a list of node IDs
   :param NodeList node_list: a JSON of nodes
   
   :returns: A list of coordinates
   :rtype: List[Coord]

   :raises KeyError: if a node does not exist"""
    coords = []
    for node_id in nodes:
        if node_id not in node_list.node_ids():
            raise KeyError(f"Node '{node_id}' does not exist")
        coords.append(Coord(node_list[node_id].x, node_list[node_id].y))
    return coords