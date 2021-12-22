from typing import Literal, Dict, List

from schema import Schema, Or

from renderer.types import RealNum, NodeListJson, NodeJson


class Node:
    """A representation of a node.

    :param NodeJson json: The JSON of the node."""
    def __init__(self, json: NodeJson):
        self.x: RealNum = json['x']
        """The ``x`` coordinate of the node."""
        self.y: RealNum = json['y']
        """The ``y`` coordinate of the node."""
        self.connections: list = json['connections']
        """Currently useless, will be used soon tm"""

class NodeList:
    """A list of nodes.

    :param NodeListJson json: The JSON of the list of nodes."""
    def __init__(self, json: NodeListJson):
        self.validate_json(json)
        self.nodes: Dict[str, Node] = {name: Node(node) for name, node in json.items()}
        """A dictionary of node objects, in the form ``{id: node}``"""

    def __getitem__(self, name: str) -> Node:
        return self.nodes[name]

    def node_ids(self) -> List[str]:
        """Gets all the node IDs.

        :rtype: List[str]"""
        return list(self.nodes.keys())

    def node_values(self) -> List[Node]:
        """Gets all the node values.

        :rtype: List[Node]"""
        return list(self.nodes.values())

    @staticmethod
    def validate_json(json: dict) -> Literal[True]:
        """
        Validates a JSON of nodes.

        :param NodeListJson json: a dictionary of nodes

        :returns: Returns True if no errors
        """
        schema = Schema({
            str: {
                "x": Or(int, float),
                "y": Or(int, float),
                "connections": list
            }
        })
        schema.validate(json)
        return True