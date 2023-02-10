from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.arrayTools import calcIntBounds as calcIntBounds
from fontTools.misc.textTools import Tag as Tag
from fontTools.misc.textTools import bytechr as bytechr
from fontTools.misc.textTools import byteord as byteord
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import pad as pad
from fontTools.ttLib import TTFont as TTFont
from fontTools.ttLib import TTLibError as TTLibError
from fontTools.ttLib import getSearchRange as getSearchRange
from fontTools.ttLib import getTableClass as getTableClass
from fontTools.ttLib import getTableModule as getTableModule
from fontTools.ttLib.sfnt import DirectoryEntry as DirectoryEntry
from fontTools.ttLib.sfnt import SFNTDirectoryEntry as SFNTDirectoryEntry
from fontTools.ttLib.sfnt import SFNTReader as SFNTReader
from fontTools.ttLib.sfnt import SFNTWriter as SFNTWriter
from fontTools.ttLib.sfnt import WOFFFlavorData as WOFFFlavorData
from fontTools.ttLib.sfnt import calcChecksum as calcChecksum
from fontTools.ttLib.sfnt import sfntDirectoryEntrySize as sfntDirectoryEntrySize
from fontTools.ttLib.sfnt import sfntDirectoryFormat as sfntDirectoryFormat
from fontTools.ttLib.sfnt import sfntDirectorySize as sfntDirectorySize
from fontTools.ttLib.tables import ttProgram as ttProgram

log: Incomplete
haveBrotli: bool

class WOFF2Reader(SFNTReader):
    flavor: str
    file: Incomplete
    DirectoryEntry: Incomplete
    tables: Incomplete
    transformBuffer: Incomplete
    flavorData: Incomplete
    ttFont: Incomplete
    def __init__(
        self, file, checkChecksums: int = ..., fontNumber: int = ...
    ) -> None: ...
    def __getitem__(self, tag): ...
    def reconstructTable(self, tag): ...

class WOFF2Writer(SFNTWriter):
    flavor: str
    file: Incomplete
    numTables: Incomplete
    sfntVersion: Incomplete
    flavorData: Incomplete
    directoryFormat: Incomplete
    directorySize: Incomplete
    DirectoryEntry: Incomplete
    signature: Incomplete
    nextTableOffset: int
    transformBuffer: Incomplete
    tables: Incomplete
    ttFont: Incomplete
    def __init__(
        self,
        file,
        numTables,
        sfntVersion: str = ...,
        flavor: Incomplete | None = ...,
        flavorData: Incomplete | None = ...,
    ) -> None: ...
    def __setitem__(self, tag, data) -> None: ...
    totalSfntSize: Incomplete
    totalCompressedSize: Incomplete
    length: Incomplete
    reserved: int
    def close(self) -> None: ...
    def transformTable(self, tag): ...
    def writeMasterChecksum(self) -> None: ...
    def reordersTables(self): ...

woff2DirectoryFormat: str
woff2DirectorySize: Incomplete
woff2KnownTags: Incomplete
woff2FlagsFormat: str
woff2FlagsSize: Incomplete
woff2UnknownTagFormat: str
woff2UnknownTagSize: Incomplete
woff2UnknownTagIndex: int
woff2Base128MaxSize: int
woff2DirectoryEntryMaxSize: Incomplete
woff2TransformedTableTags: Incomplete
woff2GlyfTableFormat: str
woff2GlyfTableFormatSize: Incomplete
bboxFormat: str

def getKnownTagIndex(tag): ...

class WOFF2DirectoryEntry(DirectoryEntry):
    def fromFile(self, file) -> None: ...
    tag: Incomplete
    length: Incomplete
    def fromString(self, data): ...
    def toString(self): ...
    @property
    def transformVersion(self): ...
    @transformVersion.setter
    def transformVersion(self, value) -> None: ...
    @property
    def transformed(self): ...
    @transformed.setter
    def transformed(self, booleanValue) -> None: ...

class WOFF2LocaTable:
    tableTag: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    def compile(self, ttFont): ...

class WOFF2GlyfTable:
    subStreams: Incomplete
    tableTag: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    bboxBitmap: Incomplete
    bboxStream: Incomplete
    nContourStream: Incomplete
    glyphOrder: Incomplete
    def reconstruct(self, data, ttFont) -> None: ...
    numGlyphs: Incomplete
    indexFormat: Incomplete
    version: int
    def transform(self, ttFont): ...

class WOFF2HmtxTable:
    tableTag: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    metrics: Incomplete
    def reconstruct(self, data, ttFont) -> None: ...
    def transform(self, ttFont): ...

class WOFF2FlavorData(WOFFFlavorData):
    Flavor: str
    majorVersion: Incomplete
    metaData: Incomplete
    privData: Incomplete
    transformedTables: Incomplete
    def __init__(
        self,
        reader: Incomplete | None = ...,
        data: Incomplete | None = ...,
        transformedTables: Incomplete | None = ...,
    ) -> None: ...

def unpackBase128(data): ...
def base128Size(n): ...
def packBase128(n): ...
def unpack255UShort(data): ...
def pack255UShort(value): ...
def compress(
    input_file, output_file, transform_tables: Incomplete | None = ...
) -> None: ...
def decompress(input_file, output_file) -> None: ...
def main(args: Incomplete | None = ...) -> None: ...
