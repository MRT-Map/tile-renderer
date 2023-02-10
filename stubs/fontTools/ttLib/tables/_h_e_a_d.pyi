from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.arrayTools import intRect as intRect
from fontTools.misc.arrayTools import unionRect as unionRect
from fontTools.misc.fixedTools import floatToFixedToStr as floatToFixedToStr
from fontTools.misc.fixedTools import strToFixedToFloat as strToFixedToFloat
from fontTools.misc.textTools import binary2num as binary2num
from fontTools.misc.textTools import num2binary as num2binary
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.timeTools import timestampFromString as timestampFromString
from fontTools.misc.timeTools import timestampNow as timestampNow
from fontTools.misc.timeTools import timestampToString as timestampToString

from . import DefaultTable as DefaultTable

log: Incomplete
headFormat: str

class table__h_e_a_d(DefaultTable.DefaultTable):
    dependencies: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    modified: Incomplete
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
