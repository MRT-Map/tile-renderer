from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

hheaFormat: str

class table__h_h_e_a(DefaultTable.DefaultTable):
    dependencies: Incomplete
    @property
    def ascender(self): ...
    ascent: Incomplete
    @ascender.setter
    def ascender(self, value) -> None: ...
    @property
    def descender(self): ...
    descent: Incomplete
    @descender.setter
    def descender(self, value) -> None: ...
    def decompile(self, data, ttFont) -> None: ...
    tableVersion: Incomplete
    def compile(self, ttFont): ...
    advanceWidthMax: Incomplete
    minLeftSideBearing: Incomplete
    minRightSideBearing: Incomplete
    xMaxExtent: Incomplete
    def recalc(self, ttFont) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
