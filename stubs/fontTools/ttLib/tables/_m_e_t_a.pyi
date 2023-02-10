from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import readHex as readHex
from fontTools.misc.textTools import strjoin as strjoin
from fontTools.ttLib import TTLibError as TTLibError

from . import DefaultTable as DefaultTable

META_HEADER_FORMAT: str
DATA_MAP_FORMAT: str

class table__m_e_t_a(DefaultTable.DefaultTable):
    data: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
