from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.fixedTools import floatToFixedToStr as floatToFixedToStr
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable
from . import grUtils as grUtils

Sill_hdr: str

class table_S__i_l_l(DefaultTable.DefaultTable):
    langs: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    version: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
