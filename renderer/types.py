from typing import Union, List, Dict, TypedDict, Literal, Any, NamedTuple

from renderer.internals import internal

try: from typing import TypeAlias
except ImportError: TypeAlias = type

RealNum: TypeAlias = Union[int, float]
"""Represents a real number, either an integer or float."""

class Coord(NamedTuple):
    """Represents a coordinate in the form ``(x, y)``."""
    x: RealNum
    y: RealNum

    def __str__(self) -> str:
        return internal._tuple_to_str((self.x, self.y))


class TileCoord(NamedTuple):
    """Represents a tile coordinate in the form ``(z, x, y)``."""
    z: int
    x: int
    y: int

    def __str__(self) -> str:
        return internal._tuple_to_str((self.z, self.x, self.y))

NodeJson = TypedDict('NodeJson', {
    'x': int,
    'y': int,
    'connections': list
})
"""Represents a node JSON object."""
NodeListJson: TypeAlias = Dict[str, NodeJson]
"""Represents a node list JSON."""

ComponentJson = TypedDict('ComponentJson', {
    'type': str,
    'displayname': str,
    'description': str,
    'layer': RealNum,
    'nodes': List[str],
    'attrs': Dict[str, Any],
    'hollows': List[List[str]]
}, total=False)
"""Represents a component JSON object."""
ComponentListJson: TypeAlias = Dict[str, ComponentJson]
"""Represents a component list JSON."""

SkinInfo = TypedDict('SkinInfo', {
    'size': int,
    'font': Dict[str, str],
    'background': str
})
"""Represents the ``info`` portion of a skin JSON."""
SkinType = TypedDict('SkinType', {
    'tags': List[str],
    'type': Literal['point', 'line', 'area'],
    'style': Dict[str, list]
})
"""Represents a component type in the ``types`` portion of a skin JSON."""
SkinJson = TypedDict('SkinJson', {
    'info': SkinInfo,
    'order': List[str],
    'types': Dict[str, SkinType]
})
"""Represents a skin JSON."""