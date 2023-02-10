from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.fixedTools import floatToFixedToStr as floatToFixedToStr
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable
from . import grUtils as grUtils

Feat_hdr_format: str

class table_F__e_a_t(DefaultTable.DefaultTable):
    features: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    version: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont): ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class Feature: ...
