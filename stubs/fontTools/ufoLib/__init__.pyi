import enum

from _typeshed import Incomplete
from fontTools.ufoLib.errors import UFOLibError as UFOLibError
from fontTools.ufoLib.utils import _VersionTupleEnumMixin
from fontTools.ufoLib.validators import *

class UFOFormatVersion(tuple, _VersionTupleEnumMixin, enum.Enum):
    FORMAT_1_0: Incomplete
    FORMAT_2_0: Incomplete
    FORMAT_3_0: Incomplete

class UFOFileStructure(enum.Enum):
    ZIP: str
    PACKAGE: str

class _UFOBaseIO:
    def getFileModificationTime(self, path): ...

class UFOReader(_UFOBaseIO):
    fs: Incomplete
    def __init__(self, path, validate: bool = ...) -> None: ...
    path: Incomplete
    formatVersion: Incomplete
    @property
    def formatVersionTuple(self): ...
    fileStructure: Incomplete
    def readBytesFromPath(self, path): ...
    def getReadFileForPath(self, path, encoding: Incomplete | None = ...): ...
    def readMetaInfo(self, validate: Incomplete | None = ...) -> None: ...
    def readGroups(self, validate: Incomplete | None = ...): ...
    def getKerningGroupConversionRenameMaps(
        self, validate: Incomplete | None = ...
    ): ...
    def readInfo(self, info, validate: Incomplete | None = ...) -> None: ...
    def readKerning(self, validate: Incomplete | None = ...): ...
    def readLib(self, validate: Incomplete | None = ...): ...
    def readFeatures(self): ...
    def getLayerNames(self, validate: Incomplete | None = ...): ...
    def getDefaultLayerName(self, validate: Incomplete | None = ...): ...
    def getGlyphSet(
        self,
        layerName: Incomplete | None = ...,
        validateRead: Incomplete | None = ...,
        validateWrite: Incomplete | None = ...,
    ): ...
    def getCharacterMapping(
        self, layerName: Incomplete | None = ..., validate: Incomplete | None = ...
    ): ...
    def getDataDirectoryListing(self): ...
    def getImageDirectoryListing(self, validate: Incomplete | None = ...): ...
    def readData(self, fileName): ...
    def readImage(self, fileName, validate: Incomplete | None = ...): ...
    def close(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_value, exc_tb) -> None: ...

class UFOWriter(UFOReader):
    fs: Incomplete
    layerContents: Incomplete
    def __init__(
        self,
        path,
        formatVersion: Incomplete | None = ...,
        fileCreator: str = ...,
        structure: Incomplete | None = ...,
        validate: bool = ...,
    ) -> None: ...
    fileCreator: Incomplete
    def copyFromReader(self, reader, sourcePath, destPath) -> None: ...
    def writeBytesToPath(self, path, data) -> None: ...
    def getFileObjectForPath(
        self, path, mode: str = ..., encoding: Incomplete | None = ...
    ): ...
    def removePath(
        self, path, force: bool = ..., removeEmptyParents: bool = ...
    ) -> None: ...
    removeFileForPath: Incomplete
    def setModificationTime(self) -> None: ...
    def setKerningGroupConversionRenameMaps(self, maps) -> None: ...
    def writeGroups(self, groups, validate: Incomplete | None = ...) -> None: ...
    def writeInfo(self, info, validate: Incomplete | None = ...) -> None: ...
    def writeKerning(self, kerning, validate: Incomplete | None = ...) -> None: ...
    def writeLib(self, libDict, validate: Incomplete | None = ...) -> None: ...
    def writeFeatures(self, features, validate: Incomplete | None = ...) -> None: ...
    def writeLayerContents(
        self, layerOrder: Incomplete | None = ..., validate: Incomplete | None = ...
    ) -> None: ...
    def getGlyphSet(
        self,
        layerName: Incomplete | None = ...,
        defaultLayer: bool = ...,
        glyphNameToFileNameFunc: Incomplete | None = ...,
        validateRead: Incomplete | None = ...,
        validateWrite: Incomplete | None = ...,
        expectContentsFile: bool = ...,
    ): ...
    def renameGlyphSet(
        self, layerName, newLayerName, defaultLayer: bool = ...
    ) -> None: ...
    def deleteGlyphSet(self, layerName) -> None: ...
    def writeData(self, fileName, data) -> None: ...
    def removeData(self, fileName) -> None: ...
    def writeImage(self, fileName, data, validate: Incomplete | None = ...) -> None: ...
    def removeImage(self, fileName, validate: Incomplete | None = ...) -> None: ...
    def copyImageFromReader(
        self, reader, sourceFileName, destFileName, validate: Incomplete | None = ...
    ) -> None: ...
    def close(self) -> None: ...

UFOReaderWriter = UFOWriter

def makeUFOPath(path): ...
def validateFontInfoVersion2ValueForAttribute(attr, value): ...
def validateFontInfoVersion3ValueForAttribute(attr, value): ...

fontInfoAttributesVersion1: Incomplete
fontInfoAttributesVersion2: Incomplete
fontInfoAttributesVersion3: Incomplete
deprecatedFontInfoAttributesVersion2: Incomplete

def convertFontInfoValueForAttributeFromVersion1ToVersion2(attr, value): ...
def convertFontInfoValueForAttributeFromVersion2ToVersion1(attr, value): ...