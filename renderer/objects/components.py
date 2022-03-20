from typing import Literal

from schema import Schema, Or, And, Optional
from tqdm import tqdm

from renderer import validate
from renderer.objects.nodes import NodeList
from renderer.types import RealNum, ComponentListJson, NodeListJson, ComponentJson


class Component:
    """A representation of a component.

    :param str name: Will set  ``name``.
    :param ComponentJson json: The JSON of the component."""

    def __init__(self, name: str, json: ComponentJson):
        self.name: str = name
        """The name of the component in the main component list."""
        self.type: str = json['type'].split(" ")[0]
        """The type of the component."""
        self.displayname: str = json['displayname']
        """The component's display name."""
        self.description: str = json['description']
        """The component's internal description."""
        self.layer: RealNum = json['layer']
        """The layer of the component."""
        self.nodes: list[str] = json['nodes']
        """The list of nodes that the component is anchored on."""
        self.hollows: list[str] = [] if 'hollows' not in json else json['hollows']
        """A list of hollow areas, if the ``type`` is ``area``."""
        self.attrs: dict = json['attrs']
        """A dictionary of attributes."""
        if len(json['type'].split(" ")) >= 1:
            self.tags: list[str] = json['type'].split(" ")[1:]
            """A list of tags appended at the end of the component's type."""
        else:
            self.tags: list[str] = []

class ComponentList:
    """A list of components.

    :param ComponentListJson component_json: The JSON of the list of components.
    :param NodeListJson node_json: The JSON of the list of nodes for validation."""
    def __init__(self, component_json: ComponentListJson, node_json: NodeListJson ):
        try: self.components: dict[str, Component] = {name: Component(name, component) for name, component in
                                                      component_json.items()}
        except Exception:
            self.validate_json(component_json, node_json)
            self.components: dict[str, Component] = {name: Component(name, component) for name, component in
                                                     component_json.items()}
        """A dictionary of component objects, in the form of ``{id: component}``."""

    def __getitem__(self, name: str) -> Component:
        return self.components[name]

    def component_ids(self) -> list[str]:
        """Gets all the component IDs.

        :rtype: list[str]"""
        return list(self.components.keys())

    def component_values(self) -> list[Component]:
        """Gets all the component values.

        :rtype: list[Component]"""
        return list(self.components.values())

    @staticmethod
    def validate_json(component_json: dict, node_json: dict) -> Literal[True]:
        """
        Validates a JSON of components.

        :param ComponentListJson component_json: a dictionary of components
        :param NodeListJson node_json: a dictionary of nodes

        :returns: Returns True if no errors
        """
        schema = Schema({
            str: {
                "type": str,
                "displayname": str,
                "description": str,
                "layer": Or(int, float),
                "nodes": And(list, lambda i: validate.v_node_list(i, NodeList(node_json))),
                Optional("hollows"): [And(list, lambda i: validate.v_node_list(i, NodeList(node_json)))],
                "attrs": dict
            }
        })
        schema.validate(component_json)
        return True