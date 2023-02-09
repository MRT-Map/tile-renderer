from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.timeTools import timestampFromString as timestampFromString
from fontTools.misc.timeTools import timestampToString as timestampToString

from . import DefaultTable as DefaultTable

FFTMFormat: str

class table_F_F_T_M_(DefaultTable.DefaultTable):
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
