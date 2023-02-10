from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.textTools import tostr as tostr

from . import DefaultTable as DefaultTable

GMAPFormat: str
GMAPRecordFormat1: str

class GMAPRecord:
    UV: Incomplete
    cid: Incomplete
    gid: Incomplete
    ggid: Incomplete
    name: Incomplete
    def __init__(
        self,
        uv: int = ...,
        cid: int = ...,
        gid: int = ...,
        ggid: int = ...,
        name: str = ...,
    ) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def compile(self, ttFont): ...

class table_G_M_A_P_(DefaultTable.DefaultTable):
    dependencies: Incomplete
    psFontName: Incomplete
    gmapRecords: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    recordsCount: Incomplete
    fontNameLength: Incomplete
    recordsOffset: Incomplete
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
