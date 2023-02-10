from typing import NamedTuple

from _typeshed import Incomplete
from fontTools import varLib as varLib
from fontTools.cffLib import FDArrayIndex as FDArrayIndex
from fontTools.cffLib import FontDict as FontDict
from fontTools.cffLib import TopDictIndex as TopDictIndex
from fontTools.cffLib import VarStoreData as VarStoreData
from fontTools.cffLib import buildOrder as buildOrder
from fontTools.cffLib import maxStackLimit as maxStackLimit
from fontTools.cffLib import privateDictOperators as privateDictOperators
from fontTools.cffLib import privateDictOperators2 as privateDictOperators2
from fontTools.cffLib import topDictOperators as topDictOperators
from fontTools.cffLib import topDictOperators2 as topDictOperators2
from fontTools.cffLib.specializer import commandsToProgram as commandsToProgram
from fontTools.cffLib.specializer import specializeCommands as specializeCommands
from fontTools.misc.psCharStrings import T2CharString as T2CharString
from fontTools.misc.psCharStrings import T2OutlineExtractor as T2OutlineExtractor
from fontTools.misc.roundTools import roundFunc as roundFunc
from fontTools.pens.t2CharStringPen import T2CharStringPen as T2CharStringPen
from fontTools.ttLib import newTable as newTable
from fontTools.varLib.models import allEqual as allEqual

from .errors import VarLibCFFDictMergeError as VarLibCFFDictMergeError
from .errors import VarLibCFFHintTypeMergeError as VarLibCFFHintTypeMergeError
from .errors import VarLibCFFPointTypeMergeError as VarLibCFFPointTypeMergeError
from .errors import VarLibMergeError as VarLibMergeError

MergeDictError = VarLibCFFDictMergeError
MergeTypeError = VarLibCFFPointTypeMergeError

def addCFFVarStore(varFont, varModel, varDataList, masterSupports) -> None: ...
def lib_convertCFFToCFF2(cff, otFont) -> None: ...
def convertCFFtoCFF2(varFont) -> None: ...
def conv_to_int(num): ...

pd_blend_fields: Incomplete

def get_private(regionFDArrays, fd_index, ri, fd_map): ...
def merge_PrivateDicts(top_dicts, vsindex_dict, var_model, fd_map) -> None: ...
def getfd_map(varFont, fonts_list): ...

class CVarData(NamedTuple):
    varDataList: Incomplete
    masterSupports: Incomplete
    vsindex_dict: Incomplete

def merge_region_fonts(varFont, model, ordered_fonts_list, glyphOrder) -> None: ...
def merge_charstrings(glyphOrder, num_masters, top_dicts, masterModel): ...

class CFFToCFF2OutlineExtractor(T2OutlineExtractor):
    width: Incomplete
    gotWidth: int
    def popallWidth(self, evenOdd: int = ...): ...

class MergeOutlineExtractor(CFFToCFF2OutlineExtractor):
    def __init__(
        self,
        pen,
        localSubrs,
        globalSubrs,
        nominalWidthX,
        defaultWidthX,
        private: Incomplete | None = ...,
        blender: Incomplete | None = ...,
    ) -> None: ...
    hintCount: Incomplete
    def countHints(self): ...
    def op_hstem(self, index) -> None: ...
    def op_vstem(self, index) -> None: ...
    def op_hstemhm(self, index) -> None: ...
    def op_vstemhm(self, index) -> None: ...
    def op_hintmask(self, index): ...
    def op_cntrmask(self, index): ...

class CFF2CharStringMergePen(T2CharStringPen):
    pt_index: int
    m_index: Incomplete
    num_masters: Incomplete
    prev_move_idx: int
    seen_moveto: bool
    glyphName: Incomplete
    round: Incomplete
    def __init__(
        self,
        default_commands,
        glyphName,
        num_masters,
        master_idx,
        roundTolerance: float = ...,
    ) -> None: ...
    def add_point(self, point_type, pt_coords) -> None: ...
    def add_hint(self, hint_type, args) -> None: ...
    def add_hintmask(self, hint_type, abs_args) -> None: ...
    def restart(self, region_idx) -> None: ...
    def getCommands(self): ...
    def reorder_blend_args(self, commands, get_delta_func): ...
    def getCharString(
        self,
        private: Incomplete | None = ...,
        globalSubrs: Incomplete | None = ...,
        var_model: Incomplete | None = ...,
        optimize: bool = ...,
    ): ...
