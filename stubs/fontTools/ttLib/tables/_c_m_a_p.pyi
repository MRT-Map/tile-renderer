from _typeshed import Incomplete
from fontTools.misc.encodingTools import getEncoding as getEncoding
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import readHex as readHex
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.ttLib import getSearchRange as getSearchRange
from fontTools.unicode import Unicode as Unicode

from . import DefaultTable as DefaultTable

log: Incomplete

class table__c_m_a_p(DefaultTable.DefaultTable):
    def getcmap(self, platformID, platEncID): ...
    def getBestCmap(self, cmapPreferences=...): ...
    def buildReversed(self): ...
    tableVersion: Incomplete
    tables: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def ensureDecompiled(self, recurse: bool = ...) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class CmapSubtable:
    @staticmethod
    def getSubtableClass(format): ...
    @staticmethod
    def newSubtable(format): ...
    format: Incomplete
    data: Incomplete
    ttFont: Incomplete
    platformID: Incomplete
    platEncID: Incomplete
    language: Incomplete
    def __init__(self, format) -> None: ...
    def ensureDecompiled(self, recurse: bool = ...) -> None: ...
    def __getattr__(self, attr): ...
    length: Incomplete
    def decompileHeader(self, data, ttFont) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def getEncoding(self, default: Incomplete | None = ...): ...
    def isUnicode(self): ...
    def isSymbol(self): ...
    def __lt__(self, other): ...

class cmap_format_0(CmapSubtable):
    cmap: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    language: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

subHeaderFormat: str

class SubHeader:
    firstCode: Incomplete
    entryCount: Incomplete
    idDelta: Incomplete
    idRangeOffset: Incomplete
    glyphIndexArray: Incomplete
    def __init__(self) -> None: ...

class cmap_format_2(CmapSubtable):
    def setIDDelta(self, subHeader) -> None: ...
    data: bytes
    cmap: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    language: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

cmap_format_4_format: str

def splitRange(startCode, endCode, cmap): ...

class cmap_format_4(CmapSubtable):
    data: Incomplete
    cmap: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    language: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class cmap_format_6(CmapSubtable):
    data: Incomplete
    cmap: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    language: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class cmap_format_12_or_13(CmapSubtable):
    format: Incomplete
    reserved: int
    data: Incomplete
    ttFont: Incomplete
    def __init__(self, format) -> None: ...
    length: Incomplete
    language: Incomplete
    nGroups: Incomplete
    def decompileHeader(self, data, ttFont) -> None: ...
    cmap: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class cmap_format_12(cmap_format_12_or_13):
    def __init__(self, format: int = ...) -> None: ...

class cmap_format_13(cmap_format_12_or_13):
    def __init__(self, format: int = ...) -> None: ...

def cvtToUVS(threeByteString): ...
def cvtFromUVS(val): ...

class cmap_format_14(CmapSubtable):
    data: Incomplete
    length: Incomplete
    numVarSelectorRecords: Incomplete
    ttFont: Incomplete
    language: int
    def decompileHeader(self, data, ttFont) -> None: ...
    cmap: Incomplete
    uvsDict: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def toXML(self, writer, ttFont): ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def compile(self, ttFont): ...

class cmap_format_unknown(CmapSubtable):
    def toXML(self, writer, ttFont) -> None: ...
    data: Incomplete
    cmap: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    language: int
    def decompileHeader(self, data, ttFont) -> None: ...
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...

cmap_classes: Incomplete
