import enum
from functools import partial as partial
from math import ceil as ceil
from math import log as log
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

from _typeshed import Incomplete
from fontTools.misc.arrayTools import intRect as intRect
from fontTools.misc.fixedTools import fixedToFloat as fixedToFloat
from fontTools.misc.treeTools import build_n_ary_tree as build_n_ary_tree
from fontTools.ttLib.tables import C_O_L_R_ as C_O_L_R_
from fontTools.ttLib.tables import C_P_A_L_ as C_P_A_L_
from fontTools.ttLib.tables import _n_a_m_e
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables.otTables import CompositeMode as CompositeMode
from fontTools.ttLib.tables.otTables import ExtendMode as ExtendMode

from .errors import ColorLibError as ColorLibError
from .geometry import (
    round_start_circle_stable_containment as round_start_circle_stable_containment,
)
from .table_builder import BuildCallback as BuildCallback
from .table_builder import TableBuilder as TableBuilder

T = TypeVar("T")
MAX_PAINT_COLR_LAYER_COUNT: int

def populateCOLRv0(
    table: ot.COLR,
    colorGlyphsV0: _ColorGlyphsV0Dict,
    glyphMap: Optional[Mapping[str, int]] = ...,
): ...
def buildCOLR(
    colorGlyphs: _ColorGlyphsDict,
    version: Optional[int] = ...,
    *,
    glyphMap: Optional[Mapping[str, int]] = ...,
    varStore: Optional[ot.VarStore] = ...,
    varIndexMap: Optional[ot.DeltaSetIndexMap] = ...,
    clipBoxes: Optional[Dict[str, _ClipBoxInput]] = ...,
    allowLayerReuse: bool = ...
) -> C_O_L_R_.table_C_O_L_R_: ...
def buildClipList(clipBoxes: Dict[str, _ClipBoxInput]) -> ot.ClipList: ...
def buildClipBox(clipBox: _ClipBoxInput) -> ot.ClipBox: ...

class ColorPaletteType(enum.IntFlag):
    USABLE_WITH_LIGHT_BACKGROUND: int
    USABLE_WITH_DARK_BACKGROUND: int

def buildPaletteLabels(
    labels: Iterable[_OptionalLocalizedString], nameTable: _n_a_m_e.table__n_a_m_e
) -> List[Optional[int]]: ...
def buildCPAL(
    palettes: Sequence[Sequence[Tuple[float, float, float, float]]],
    paletteTypes: Optional[Sequence[ColorPaletteType]] = ...,
    paletteLabels: Optional[Sequence[_OptionalLocalizedString]] = ...,
    paletteEntryLabels: Optional[Sequence[_OptionalLocalizedString]] = ...,
    nameTable: Optional[_n_a_m_e.table__n_a_m_e] = ...,
) -> C_P_A_L_.table_C_P_A_L_: ...

class LayerReuseCache:
    reusePool: Mapping[Tuple[Any, ...], int]
    tuples: Mapping[int, Tuple[Any, ...]]
    keepAlive: List[ot.Paint]
    def __init__(self) -> None: ...
    def try_reuse(self, layers: List[ot.Paint]) -> List[ot.Paint]: ...
    def add(self, layers: List[ot.Paint], first_layer_index: int): ...

class LayerListBuilder:
    layers: List[ot.Paint]
    cache: LayerReuseCache
    allowLayerReuse: bool
    tableBuilder: Incomplete
    def __init__(self, *, allowLayerReuse: bool = ...) -> None: ...
    def buildPaint(self, paint: _PaintInput) -> ot.Paint: ...
    def build(self) -> Optional[ot.LayerList]: ...

def buildBaseGlyphPaintRecord(
    baseGlyph: str, layerBuilder: LayerListBuilder, paint: _PaintInput
) -> ot.BaseGlyphList: ...
def buildColrV1(
    colorGlyphs: _ColorGlyphsDict,
    glyphMap: Optional[Mapping[str, int]] = ...,
    *,
    allowLayerReuse: bool = ...
) -> Tuple[Optional[ot.LayerList], ot.BaseGlyphList]: ...
