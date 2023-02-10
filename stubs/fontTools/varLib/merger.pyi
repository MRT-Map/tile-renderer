from _typeshed import Incomplete
from fontTools.colorLib.builder import (
    MAX_PAINT_COLR_LAYER_COUNT as MAX_PAINT_COLR_LAYER_COUNT,
)
from fontTools.colorLib.builder import LayerReuseCache as LayerReuseCache
from fontTools.misc import classifyTools as classifyTools
from fontTools.misc.roundTools import otRound as otRound
from fontTools.misc.treeTools import build_n_ary_tree as build_n_ary_tree
from fontTools.otlLib.builder import buildSinglePos as buildSinglePos
from fontTools.otlLib.optimize.gpos import compact_pair_pos as compact_pair_pos
from fontTools.ttLib.tables.DefaultTable import DefaultTable as DefaultTable
from fontTools.ttLib.tables.otConverters import BaseFixedValue as BaseFixedValue
from fontTools.ttLib.tables.otTraverse import dfs_base_table as dfs_base_table
from fontTools.varLib import builder as builder
from fontTools.varLib import models as models
from fontTools.varLib import varStore as varStore
from fontTools.varLib.models import allEqual as allEqual
from fontTools.varLib.models import allEqualTo as allEqualTo
from fontTools.varLib.models import allNone as allNone
from fontTools.varLib.models import nonNone as nonNone
from fontTools.varLib.models import subList as subList
from fontTools.varLib.varStore import VarStoreInstancer as VarStoreInstancer

from .errors import FoundANone as FoundANone
from .errors import InconsistentExtensions as InconsistentExtensions
from .errors import InconsistentFormats as InconsistentFormats
from .errors import InconsistentGlyphOrder as InconsistentGlyphOrder
from .errors import KeysDiffer as KeysDiffer
from .errors import LengthsDiffer as LengthsDiffer
from .errors import MismatchedTypes as MismatchedTypes
from .errors import NotANone as NotANone
from .errors import ShouldBeConstant as ShouldBeConstant
from .errors import UnsupportedFormat as UnsupportedFormat
from .errors import VarLibMergeError as VarLibMergeError

log: Incomplete

class Merger:
    font: Incomplete
    ttfs: Incomplete
    def __init__(self, font: Incomplete | None = ...) -> None: ...
    @classmethod
    def merger(celf, clazzes, attrs=...): ...
    @classmethod
    def mergersFor(celf, thing, _default=...): ...
    def mergeObjects(self, out, lst, exclude=...) -> None: ...
    def mergeLists(self, out, lst) -> None: ...
    def mergeThings(self, out, lst) -> None: ...
    def mergeTables(self, font, master_ttfs, tableTags) -> None: ...

class AligningMerger(Merger): ...

def merge(merger, self, lst) -> None: ...

class InstancerMerger(AligningMerger):
    model: Incomplete
    location: Incomplete
    scalars: Incomplete
    def __init__(self, font, model, location) -> None: ...

class MutatorMerger(AligningMerger):
    instancer: Incomplete
    deleteVariations: Incomplete
    def __init__(self, font, instancer, deleteVariations: bool = ...) -> None: ...

class VariationMerger(AligningMerger):
    store_builder: Incomplete
    def __init__(self, model, axisTags, font) -> None: ...
    model: Incomplete
    def setModel(self, model) -> None: ...
    ttfs: Incomplete
    def mergeThings(self, out, lst) -> None: ...

def buildVarDevTable(store_builder, master_values): ...

class COLRVariationMerger(VariationMerger):
    varIndexCache: Incomplete
    varIdxes: Incomplete
    varTableIds: Incomplete
    layers: Incomplete
    layerReuseCache: Incomplete
    def __init__(self, model, axisTags, font, allowLayerReuse: bool = ...) -> None: ...
    def mergeTables(self, font, master_ttfs, tableTags=...) -> None: ...
    def checkFormatEnum(self, out, lst, validate=...): ...
    def mergeSparseDict(self, out, lst) -> None: ...
    def mergeAttrs(self, out, lst, attrs) -> None: ...
    def storeMastersForAttr(self, out, lst, attr): ...
    def storeVariationIndices(self, varIdxes) -> int: ...
    def mergeVariableAttrs(self, out, lst, attrs) -> int: ...
    @classmethod
    def convertSubTablesToVarType(cls, table): ...
    @staticmethod
    def expandPaintColrLayers(colr) -> None: ...
