from typing import Any, Literal, TypeAlias, TypedDict


class Pla1NodeJson(TypedDict):
    """Represents a node JSON object."""

    x: int
    y: int
    connections: list


Pla1NodeListJson: TypeAlias = dict[str, Pla1NodeJson]
"""Represents a node list JSON."""


class Pla1ComponentJson(TypedDict, total=False):
    """Represents a component JSON object."""

    type: str
    displayname: str
    description: str
    layer: float
    nodes: list[str]
    attrs: dict[str, Any]
    hollows: list[list[str]]


Pla1ComponentListJson: TypeAlias = dict[str, Pla1ComponentJson]
"""Represents a component list JSON."""


class SkinInfo(TypedDict):
    """Represents the ``info`` portion of a skin JSON."""

    size: int
    font: dict[str, str]
    background: str


class SkinType(TypedDict):
    """Represents a component type in the ``types`` portion of a skin JSON."""

    tags: list[str]
    type: Literal["point", "line", "area"]
    style: dict[str, list]


class SkinJson(TypedDict):
    """Represents a skin JSON."""

    info: SkinInfo
    order: list[str]
    types: dict[str, SkinType]
