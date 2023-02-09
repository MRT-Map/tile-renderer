from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.ttLib import TTLibError as TTLibError

from . import DefaultTable as DefaultTable

log: Incomplete
AVAR_HEADER_FORMAT: str

class table__a_v_a_r(DefaultTable.DefaultTable):
    dependencies: Incomplete
    segments: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    def compile(self, ttFont): ...
    def decompile(self, data, ttFont) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
