from _typeshed import Incomplete
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

class table_T_S_I__5(DefaultTable.DefaultTable):
    glyphGrouping: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...