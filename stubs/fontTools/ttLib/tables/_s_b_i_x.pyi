from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import binary2num as binary2num
from fontTools.misc.textTools import num2binary as num2binary
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable
from .sbixStrike import Strike as Strike

sbixHeaderFormat: str
sbixHeaderFormatSize: Incomplete
sbixStrikeOffsetFormat: str
sbixStrikeOffsetFormatSize: Incomplete

class table__s_b_i_x(DefaultTable.DefaultTable):
    version: int
    flags: int
    numStrikes: int
    strikes: Incomplete
    strikeOffsets: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, xmlWriter, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class sbixStrikeOffset: ...
