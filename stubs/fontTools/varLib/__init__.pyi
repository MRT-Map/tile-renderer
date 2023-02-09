from typing import NamedTuple

from _typeshed import Incomplete
from fontTools.colorLib.builder import buildColrV1 as buildColrV1
from fontTools.colorLib.unbuilder import unbuildColrV1 as unbuildColrV1
from fontTools.designspaceLib import DesignSpaceDocument as DesignSpaceDocument
from fontTools.designspaceLib import InstanceDescriptor as InstanceDescriptor
from fontTools.designspaceLib.split import splitInterpolable as splitInterpolable
from fontTools.designspaceLib.split import splitVariableFonts as splitVariableFonts
from fontTools.misc.roundTools import noRound as noRound
from fontTools.misc.roundTools import otRound as otRound
from fontTools.misc.textTools import Tag as Tag
from fontTools.misc.textTools import tostr as tostr
from fontTools.misc.vector import Vector as Vector
from fontTools.ttLib import TTFont as TTFont
from fontTools.ttLib import newTable as newTable
from fontTools.ttLib.tables._f_v_a_r import Axis as Axis
from fontTools.ttLib.tables._f_v_a_r import NamedInstance as NamedInstance
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates as GlyphCoordinates
from fontTools.ttLib.tables.otBase import OTTableWriter as OTTableWriter
from fontTools.ttLib.tables.ttProgram import Program as Program
from fontTools.ttLib.tables.TupleVariation import TupleVariation as TupleVariation
from fontTools.varLib import builder as builder
from fontTools.varLib import models as models
from fontTools.varLib import varStore as varStore
from fontTools.varLib.featureVars import addFeatureVariations as addFeatureVariations
from fontTools.varLib.iup import iup_delta_optimize as iup_delta_optimize
from fontTools.varLib.merger import COLRVariationMerger as COLRVariationMerger
from fontTools.varLib.merger import VariationMerger as VariationMerger
from fontTools.varLib.mvar import MVAR_ENTRIES as MVAR_ENTRIES
from fontTools.varLib.stat import buildVFStatTable as buildVFStatTable

from .errors import VarLibError as VarLibError
from .errors import VarLibValidationError as VarLibValidationError

log: Incomplete
FEAVAR_FEATURETAG_LIB_KEY: str

class _MasterData(NamedTuple):
    glyf: Incomplete
    hMetrics: Incomplete
    vMetrics: Incomplete

class _MetricsFields(NamedTuple):
    tableTag: Incomplete
    metricsTag: Incomplete
    sb1: Incomplete
    sb2: Incomplete
    advMapping: Incomplete
    vOrigMapping: Incomplete

HVAR_FIELDS: Incomplete
VVAR_FIELDS: Incomplete

class _DesignSpaceData(NamedTuple):
    axes: Incomplete
    internal_axis_supports: Incomplete
    base_idx: Incomplete
    normalized_master_locs: Incomplete
    masters: Incomplete
    instances: Incomplete
    rules: Incomplete
    rulesProcessingLast: Incomplete
    lib: Incomplete

def load_designspace(designspace): ...

WDTH_VALUE_TO_OS2_WIDTH_CLASS: Incomplete

def set_default_weight_width_slant(font, location) -> None: ...
def build_many(
    designspace: DesignSpaceDocument,
    master_finder=...,
    exclude=...,
    optimize: bool = ...,
    skip_vf=...,
    colr_layer_reuse: bool = ...,
): ...
def build(
    designspace,
    master_finder=...,
    exclude=...,
    optimize: bool = ...,
    colr_layer_reuse: bool = ...,
): ...
def load_masters(designspace, master_finder=...): ...

class MasterFinder:
    template: Incomplete
    def __init__(self, template) -> None: ...
    def __call__(self, src_path): ...

def main(args: Incomplete | None = ...) -> None: ...
