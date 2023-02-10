from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import readHex as readHex
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

GPKGFormat: str

class table_G_P_K_G_(DefaultTable.DefaultTable):
    GMAPs: Incomplete
    glyphlets: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    numGMAPs: Incomplete
    numGlyplets: Incomplete
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
