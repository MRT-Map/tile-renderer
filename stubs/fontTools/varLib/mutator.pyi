from _typeshed import Incomplete
from fontTools.misc.fixedTools import floatToFixed as floatToFixed
from fontTools.misc.fixedTools import floatToFixedToFloat as floatToFixedToFloat
from fontTools.misc.roundTools import otRound as otRound
from fontTools.pens.boundsPen import BoundsPen as BoundsPen
from fontTools.ttLib import TTFont as TTFont
from fontTools.ttLib import newTable as newTable
from fontTools.ttLib.tables import ttProgram as ttProgram
from fontTools.ttLib.tables._g_l_y_f import OVERLAP_COMPOUND as OVERLAP_COMPOUND
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates as GlyphCoordinates
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple as flagOverlapSimple
from fontTools.varLib.iup import iup_delta as iup_delta
from fontTools.varLib.merger import MutatorMerger as MutatorMerger
from fontTools.varLib.models import normalizeLocation as normalizeLocation
from fontTools.varLib.models import piecewiseLinearMap as piecewiseLinearMap
from fontTools.varLib.models import supportScalar as supportScalar
from fontTools.varLib.mvar import MVAR_ENTRIES as MVAR_ENTRIES
from fontTools.varLib.varStore import VarStoreInstancer as VarStoreInstancer

log: Incomplete
OS2_WIDTH_CLASS_VALUES: Incomplete
percents: Incomplete
half: Incomplete

def interpolate_cff2_PrivateDict(topDict, interpolateFromDeltas) -> None: ...
def interpolate_cff2_charstrings(
    topDict, interpolateFromDeltas, glyphOrder
) -> None: ...
def interpolate_cff2_metrics(varfont, topDict, glyphOrder, loc) -> None: ...
def instantiateVariableFont(
    varfont, location, inplace: bool = ..., overlap: bool = ...
): ...
def main(args: Incomplete | None = ...) -> None: ...
