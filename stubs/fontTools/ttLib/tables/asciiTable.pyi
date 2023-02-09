from _typeshed import Incomplete
from fontTools.misc.textTools import strjoin as strjoin
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.textTools import tostr as tostr

from . import DefaultTable as DefaultTable

class asciiTable(DefaultTable.DefaultTable):
    def toXML(self, writer, ttFont) -> None: ...
    data: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
