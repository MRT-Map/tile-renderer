from typing import Literal, Dict, List

from schema import Schema, Or

from renderer.types import RealNum, NodeJson


class Node:
    def __init__(self, json: dict):
        self.x: RealNum = json['x']
        self.y: RealNum = json['y']
        self.connections: list = json['connections']

class NodeList:
    def __init__(self, json: NodeJson):
        self.validate_json(json)
        self.nodes: Dict[str, Node] = {name: Node(node) for name, node in json}

    def __getitem__(self, name: str) -> Node:
        return self.nodes[name]

    def node_ids(self) -> List[str]:
        return list(self.nodes.keys())

    def node_values(self) -> List[Node]:
        return list(self.nodes.values())

    @staticmethod
    def validate_json(json: dict) -> Literal[True]:
        """
        Validates a JSON of nodes.

        :param NodeJson json: a dictionary of nodes

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