from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

maxpFormat_0_5: str
maxpFormat_1_0_add: str

class table__m_a_x_p(DefaultTable.DefaultTable):
    dependencies: Incomplete
    numGlyphs: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    tableVersion: int
    def compile(self, ttFont): ...
    maxPoints: Incomplete
    maxContours: Incomplete
    maxCompositePoints: Incomplete
    maxCompositeContours: Incomplete
    maxComponentElements: Incomplete
    maxComponentDepth: Incomplete
    def recalc(self, ttFont) -> None: ...
    def testrepr(self) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
