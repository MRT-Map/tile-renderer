from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import Tag as Tag
from fontTools.ttLib import TTLibError as TTLibError

log: Incomplete

class SFNTReader:
    def __new__(cls, *args, **kwargs): ...
    file: Incomplete
    checkChecksums: Incomplete
    flavor: Incomplete
    flavorData: Incomplete
    DirectoryEntry: Incomplete
    sfntVersion: Incomplete
    numFonts: Incomplete
    tables: Incomplete
    def __init__(
        self, file, checkChecksums: int = ..., fontNumber: int = ...
    ) -> None: ...
    def has_key(self, tag): ...
    __contains__: Incomplete
    def keys(self): ...
    def __getitem__(self, tag): ...
    def __delitem__(self, tag) -> None: ...
    def close(self) -> None: ...

ZLIB_COMPRESSION_LEVEL: int
USE_ZOPFLI: bool
ZOPFLI_LEVELS: Incomplete

def compress(data, level=...): ...

class SFNTWriter:
    def __new__(cls, *args, **kwargs): ...
    file: Incomplete
    numTables: Incomplete
    sfntVersion: Incomplete
    flavor: Incomplete
    flavorData: Incomplete
    directoryFormat: Incomplete
    directorySize: Incomplete
    DirectoryEntry: Incomplete
    signature: str
    origNextTableOffset: Incomplete
    directoryOffset: Incomplete
    nextTableOffset: Incomplete
    tables: Incomplete
    def __init__(
        self,
        file,
        numTables,
        sfntVersion: str = ...,
        flavor: Incomplete | None = ...,
        flavorData: Incomplete | None = ...,
    ) -> None: ...
    def setEntry(self, tag, entry) -> None: ...
    headTable: Incomplete
    def __setitem__(self, tag, data) -> None: ...
    def __getitem__(self, tag): ...
    reserved: int
    totalSfntSize: int
    majorVersion: Incomplete
    minorVersion: Incomplete
    metaOrigLength: Incomplete
    metaOffset: Incomplete
    metaLength: Incomplete
    privOffset: Incomplete
    privLength: Incomplete
    length: Incomplete
    def close(self) -> None: ...
    def writeMasterChecksum(self, directory) -> None: ...
    def reordersTables(self): ...

ttcHeaderFormat: str
ttcHeaderSize: Incomplete
sfntDirectoryFormat: str
sfntDirectorySize: Incomplete
sfntDirectoryEntryFormat: str
sfntDirectoryEntrySize: Incomplete
woffDirectoryFormat: str
woffDirectorySize: Incomplete
woffDirectoryEntryFormat: str
woffDirectoryEntrySize: Incomplete

class DirectoryEntry:
    uncompressed: bool
    def __init__(self) -> None: ...
    def fromFile(self, file) -> None: ...
    def fromString(self, str) -> None: ...
    def toString(self): ...
    def loadData(self, file): ...
    length: Incomplete
    def saveData(self, file, data) -> None: ...
    def decodeData(self, rawData): ...
    def encodeData(self, data): ...

class SFNTDirectoryEntry(DirectoryEntry):
    format: Incomplete
    formatSize: Incomplete

class WOFFDirectoryEntry(DirectoryEntry):
    format: Incomplete
    formatSize: Incomplete
    zlibCompressionLevel: Incomplete
    def __init__(self) -> None: ...
    def decodeData(self, rawData): ...
    origLength: Incomplete
    length: Incomplete
    def encodeData(self, data): ...

class WOFFFlavorData:
    Flavor: str
    majorVersion: Incomplete
    minorVersion: Incomplete
    metaData: Incomplete
    privData: Incomplete
    def __init__(self, reader: Incomplete | None = ...) -> None: ...

def calcChecksum(data): ...
def readTTCHeader(file): ...
def writeTTCHeader(file, numFonts): ...
