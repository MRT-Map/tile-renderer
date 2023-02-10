from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytechr as bytechr
from fontTools.misc.textTools import byteord as byteord
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.textTools import tostr as tostr

from . import DefaultTable as DefaultTable

SINGFormat: str

class table_S_I_N_G_(DefaultTable.DefaultTable):
    dependencies: Incomplete
    uniqueName: Incomplete
    nameLength: Incomplete
    baseGlyphName: Incomplete
    METAMD5: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def decompileUniqueName(self, data): ...
    def compile(self, ttFont): ...
    def compilecompileUniqueName(self, name, length): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
