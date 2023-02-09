from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

VDMX_HeaderFmt: str
VDMX_RatRangeFmt: str
VDMX_GroupFmt: str
VDMX_vTableFmt: str

class table_V_D_M_X_(DefaultTable.DefaultTable):
    ratRanges: Incomplete
    groups: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    version: Incomplete
    numRatios: int
    numRecs: int
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
