from typing import Any, Literal, TypedDict, Union

try:
    from typing import TypeAlias
except ImportError:
    TypeAlias = type

Pla1NodeJson = TypedDict("Pla1NodeJson", {"x": int, "y": int, "connections": list})
"""Represents a node JSON object."""
Pla1NodeListJson: TypeAlias = dict[str, Pla1NodeJson]
"""Represents a node list JSON."""

Pla1ComponentJson = TypedDict(
    "Pla1ComponentJson",
    {
        "type": str,
        "displayname": str,
        "description": str,
        "layer": float,
        "nodes": list[str],
        "attrs": dict[str, Any],
        "hollows": list[list[str]],
    },
    total=False,
)
"""Represents a component JSON object."""
Pla1ComponentListJson: TypeAlias = dict[str, Pla1ComponentJson]
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
