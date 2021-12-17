from typing import Union, Tuple, List, Dict, TypedDict, Literal, Any, NewType
try: from typing import TypeAlias
except ImportError: TypeAlias = type

RealNum: TypeAlias = Union[int, float]
Coord: TypeAlias = Tuple[RealNum, RealNum]
TileCoord: TypeAlias = Tuple[int, int, int]

Node = TypedDict('Node', {
    'x': int,
    'y': int,
    'connections': list
})
NodeJson: TypeAlias = Dict[str, Node]

Component = TypedDict('Component', {
    'type': str,
    'displayname': str,
    'description': str,
    'layer': RealNum,
    'nodes': List[str],
    'attrs': Dict[str, Any],
    'hollows': List[List[str]]
}, total=False)
ComponentJson: TypeAlias = Dict[str, Component]

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