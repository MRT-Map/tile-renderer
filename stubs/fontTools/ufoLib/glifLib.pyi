import enum

from _typeshed import Incomplete
from fontTools.pens.pointPen import AbstractPointPen
from fontTools.ufoLib import _UFOBaseIO
from fontTools.ufoLib.errors import GlifLibError as GlifLibError
from fontTools.ufoLib.utils import _VersionTupleEnumMixin

class GLIFFormatVersion(tuple, _VersionTupleEnumMixin, enum.Enum):
    FORMAT_1_0: Incomplete
    FORMAT_2_0: Incomplete
    @classmethod
    def default(cls, ufoFormatVersion: Incomplete | None = ...): ...
    @classmethod
    def supported_versions(cls, ufoFormatVersion: Incomplete | None = ...): ...

class Glyph:
    glyphName: Incomplete
    glyphSet: Incomplete
    def __init__(self, glyphName, glyphSet) -> None: ...
    def draw(self, pen, outputImpliedClosingLine: bool = ...) -> None: ...
    def drawPoints(self, pointPen) -> None: ...

class GlyphSet(_UFOBaseIO):
    glyphClass: Incomplete
    dirName: Incomplete
    fs: Incomplete
    ufoFormatVersion: Incomplete
    ufoFormatVersionTuple: Incomplete
    glyphNameToFileName: Incomplete
    def __init__(
        self,
        path,
        glyphNameToFileNameFunc: Incomplete | None = ...,
        ufoFormatVersion: Incomplete | None = ...,
        validateRead: bool = ...,
        validateWrite: bool = ...,
        expectContentsFile: bool = ...,
    ) -> None: ...
    contents: Incomplete
    def rebuildContents(self, validateRead: Incomplete | None = ...) -> None: ...
    def getReverseContents(self): ...
    def writeContents(self) -> None: ...
    def readLayerInfo(self, info, validateRead: Incomplete | None = ...) -> None: ...
    def writeLayerInfo(self, info, validateWrite: Incomplete | None = ...) -> None: ...
    def getGLIF(self, glyphName): ...
    def getGLIFModificationTime(self, glyphName): ...
    def readGlyph(
        self,
        glyphName,
        glyphObject: Incomplete | None = ...,
        pointPen: Incomplete | None = ...,
        validate: Incomplete | None = ...,
    ) -> None: ...
    def writeGlyph(
        self,
        glyphName,
        glyphObject: Incomplete | None = ...,
        drawPointsFunc: Incomplete | None = ...,
        formatVersion: Incomplete | None = ...,
        validate: Incomplete | None = ...,
    ) -> None: ...
    def deleteGlyph(self, glyphName) -> None: ...
    def keys(self): ...
    def has_key(self, glyphName): ...
    __contains__: Incomplete
    def __len__(self) -> int: ...
    def __getitem__(self, glyphName): ...
    def getUnicodes(self, glyphNames: Incomplete | None = ...): ...
    def getComponentReferences(self, glyphNames: Incomplete | None = ...): ...
    def getImageReferences(self, glyphNames: Incomplete | None = ...): ...
    def close(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_value, exc_tb) -> None: ...

def glyphNameToFileName(glyphName, existingFileNames): ...
def readGlyphFromString(
    aString,
    glyphObject: Incomplete | None = ...,
    pointPen: Incomplete | None = ...,
    formatVersions: Incomplete | None = ...,
    validate: bool = ...,
) -> None: ...
def writeGlyphToString(
    glyphName,
    glyphObject: Incomplete | None = ...,
    drawPointsFunc: Incomplete | None = ...,
    formatVersion: Incomplete | None = ...,
    validate: bool = ...,
): ...

class _DoneParsing(Exception): ...

class _BaseParser:
    def __init__(self) -> None: ...
    def parse(self, text) -> None: ...
    def startElementHandler(self, name, attrs) -> None: ...
    def endElementHandler(self, name) -> None: ...

class _FetchUnicodesParser(_BaseParser):
    unicodes: Incomplete
    def __init__(self) -> None: ...
    def startElementHandler(self, name, attrs) -> None: ...

class _FetchImageFileNameParser(_BaseParser):
    fileName: Incomplete
    def __init__(self) -> None: ...
    def startElementHandler(self, name, attrs) -> None: ...

class _FetchComponentBasesParser(_BaseParser):
    bases: Incomplete
    def __init__(self) -> None: ...
    def startElementHandler(self, name, attrs) -> None: ...
    def endElementHandler(self, name) -> None: ...

class GLIFPointPen(AbstractPointPen):
    formatVersion: Incomplete
    identifiers: Incomplete
    outline: Incomplete
    contour: Incomplete
    prevOffCurveCount: int
    prevPointTypes: Incomplete
    validate: Incomplete
    def __init__(
        self,
        element,
        formatVersion: Incomplete | None = ...,
        identifiers: Incomplete | None = ...,
        validate: bool = ...,
    ) -> None: ...
    def beginPath(self, identifier: Incomplete | None = ..., **kwargs) -> None: ...
    prevPointType: Incomplete
    def endPath(self) -> None: ...
    def addPoint(
        self,
        pt,
        segmentType: Incomplete | None = ...,
        smooth: Incomplete | None = ...,
        name: Incomplete | None = ...,
        identifier: Incomplete | None = ...,
        **kwargs
    ) -> None: ...
    def addComponent(
        self, glyphName, transformation, identifier: Incomplete | None = ..., **kwargs
    ) -> None: ...
