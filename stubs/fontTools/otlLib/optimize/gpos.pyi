from typing import Dict, List, NamedTuple, Sequence, Tuple

from _typeshed import Incomplete
from fontTools.config import OPTIONS as OPTIONS
from fontTools.misc.intTools import bit_count as bit_count
from fontTools.misc.intTools import bit_indices as bit_indices
from fontTools.ttLib import TTFont as TTFont
from fontTools.ttLib.tables import otBase as otBase
from fontTools.ttLib.tables import otTables as otTables

log: Incomplete
COMPRESSION_LEVEL: Incomplete
GPOS_COMPACT_MODE_ENV_KEY: str
GPOS_COMPACT_MODE_DEFAULT: Incomplete

def compact(font: TTFont, level: int) -> TTFont: ...
def compact_lookup(font: TTFont, level: int, lookup: otTables.Lookup) -> None: ...
def compact_ext_lookup(font: TTFont, level: int, lookup: otTables.Lookup) -> None: ...
def compact_pair_pos(
    font: TTFont, level: int, subtables: Sequence[otTables.PairPos]
) -> Sequence[otTables.PairPos]: ...
def compact_class_pairs(
    font: TTFont, level: int, subtable: otTables.PairPos
) -> List[otTables.PairPos]: ...
def is_really_zero(class2: otTables.Class2Record) -> bool: ...

Pairs = Dict[
    Tuple[Tuple[str, ...], Tuple[str, ...]],
    Tuple[otBase.ValueRecord, otBase.ValueRecord],
]

class ClusteringContext(NamedTuple):
    lines: Incomplete
    all_class1: Incomplete
    all_class1_data: Incomplete
    all_class2_data: Incomplete
    valueFormat1_bytes: Incomplete
    valueFormat2_bytes: Incomplete

class Cluster:
    ctx: Incomplete
    indices_bitmask: Incomplete
    def __init__(self, ctx: ClusteringContext, indices_bitmask: int) -> None: ...
    @property
    def indices(self): ...
    @property
    def column_indices(self): ...
    @property
    def width(self): ...
    @property
    def cost(self): ...
    @property
    def coverage_bytes(self): ...
    @property
    def classDef1_bytes(self): ...
    @property
    def classDef2_bytes(self): ...

def cluster_pairs_by_class2_coverage_custom_cost(
    font: TTFont, pairs: Pairs, compression: int = ...
) -> List[Pairs]: ...
