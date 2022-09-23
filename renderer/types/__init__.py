from typing import Any, Literal, TypedDict, Union

try:
    from typing import TypeAlias
except ImportError:
    TypeAlias = type

RealNum: TypeAlias = Union[int, float]
"""Represents a real number, either an integer or float."""

NodeJson = TypedDict("NodeJson", {"x": int, "y": int, "connections": list})
"""Represents a node JSON object."""
NodeListJson: TypeAlias = dict[str, NodeJson]
"""Represents a node list JSON."""

ComponentJson = TypedDict(
    "ComponentJson",
    {
        "type": str,
        "displayname": str,
        "description": str,
        "layer": RealNum,
        "nodes": list[str],
        "attrs": dict[str, Any],
        "hollows": list[list[str]],
    },
    total=False,
)
"""Represents a component JSON object."""
ComponentListJson: TypeAlias = dict[str, ComponentJson]
"""Represents a component list JSON."""

SkinInfo = TypedDict(
    "SkinInfo", {"size": int, "font": dict[str, str], "background": str}
)
"""Represents the ``info`` portion of a skin JSON."""
SkinType = TypedDict(
    "SkinType",
    {
        "tags": list[str],
        "type": Literal["point", "line", "area"],
        "style": dict[str, list],
    },
)
"""Represents a component type in the ``types`` portion of a skin JSON."""
SkinJson = TypedDict(
    "SkinJson", {"info": SkinInfo, "order": list[str], "types": dict[str, SkinType]}
)
"""Represents a skin JSON."""
