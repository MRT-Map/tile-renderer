from typing import List, Dict

from schema import Schema, Or, And, Optional

from renderer import validate
from renderer.types import RealNum, ComponentJson, NodeJson


class Component:
    def __init__(self, name: str, json: dict):
        self.name = name
        self.type: str = json['type'].split(" ")[0]
        self.displayname: str = json['displayname']
        self.description: str = json['description']
        self.layer: RealNum = json['layer']
        self.nodes: list[str] = json['nodes']
        self.hollows: List[str] = [] if 'hollows' not in json else json['hollows']
        self.attrs: dict = json['attrs']
        if len(json['type'].split(" ")) >= 1:
            self.tags: List[str] = json['type'].split(" ")[1:]
        else:
            self.tags: List[str] = []

class ComponentList:
    def __init__(self, component_json: ComponentJson, node_json: NodeJson):
        self.validate_json(component_json, node_json)
        self.components: Dict[str, Component] = {name: Component(name, component) for name, component in component_json.items()}

    def __getitem__(self, name: str) -> Component:
        return self.components[name]

    def component_ids(self) -> List[str]:
        return list(self.components.keys())

    def component_values(self) -> List[Component]:
        return list(self.components.values())

    @staticmethod
    def validate_json(component_json: dict, node_json: dict):
        """
        Validates a JSON of components.

        :param ComponentJson component_json: a dictionary of components
        :param NodeJson node_json: a dictionary of nodes

        :returns: Returns True if no errors
        """
        schema = Schema({
            str: {
                "type": str,
                "displayname": str,
                "description": str,
                "layer": Or(int, float),
                "nodes": And(list, lambda i: validate.v_node_list(i, node_json)),
                Optional("hollows"): [And(list, lambda i: validate.v_node_list(i, node_json))],
                "attrs": dict
            }
        })
        schema.validate(component_json)
        return True