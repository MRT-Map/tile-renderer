from _typeshed import Incomplete
from fontTools import cffLib as cffLib

from . import DefaultTable as DefaultTable

class table_C_F_F_(DefaultTable.DefaultTable):
    cff: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    def decompile(self, data, otFont) -> None: ...
    def compile(self, otFont): ...
    def haveGlyphNames(self): ...
    def getGlyphOrder(self): ...
    def setGlyphOrder(self, glyphOrder) -> None: ...
    def toXML(self, writer, otFont) -> None: ...
    def fromXML(self, name, attrs, content, otFont) -> None: ...