from typing import Union, List, Dict, TypedDict, Literal, Any, NamedTuple

from renderer.internals import internal

try: from typing import TypeAlias
except ImportError: TypeAlias = type

RealNum: TypeAlias = Union[int, float]

class Coord(NamedTuple):
    x: RealNum
    y: RealNum

    def __str__(self) -> str:
        return internal._tuple_to_str((self.x, self.y))


class TileCoord(NamedTuple):
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
NodeListJson: TypeAlias = Dict[str, NodeJson]

ComponentJson = TypedDict('ComponentJson', {
    'type': str,
    'displayname': str,
    'description': str,
    'layer': RealNum,
    'nodes': List[str],
    'attrs': Dict[str, Any],
    'hollows': List[List[str]]
}, total=False)
ComponentListJson: TypeAlias = Dict[str, ComponentJson]

SkinInfo = TypedDict('SkinInfo', {
    'size': int,
    'font': Dict[str, str],
    'background': List[int]
})
SkinType = TypedDict('SkinType', {
    'tags': List[str],
    'type': Literal['point', 'line', 'area'],
    'style': Dict[str, dict]
})
SkinJson = TypedDict('SkinJson', {
    'info': SkinInfo,
    'order': List[str],
    'types': Dict[str, SkinType]
})