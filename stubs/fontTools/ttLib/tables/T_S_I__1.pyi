from _typeshed import Incomplete
from fontTools.misc.loggingTools import LogMixin as LogMixin
from fontTools.misc.textTools import strjoin as strjoin
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.textTools import tostr as tostr

from . import DefaultTable as DefaultTable

class table_T_S_I__1(LogMixin, DefaultTable.DefaultTable):
    extras: Incomplete
    indextable: str
    extraPrograms: Incomplete
    glyphPrograms: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
