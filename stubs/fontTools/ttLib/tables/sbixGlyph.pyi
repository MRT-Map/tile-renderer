from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import readHex as readHex
from fontTools.misc.textTools import safeEval as safeEval

sbixGlyphHeaderFormat: str
sbixGlyphHeaderFormatSize: Incomplete

class Glyph:
    gid: Incomplete
    glyphName: Incomplete
    referenceGlyphName: Incomplete
    originOffsetX: Incomplete
    originOffsetY: Incomplete
    rawdata: Incomplete
    graphicType: Incomplete
    imageData: Incomplete
    def __init__(
        self,
        glyphName: Incomplete | None = ...,
        referenceGlyphName: Incomplete | None = ...,
        originOffsetX: int = ...,
        originOffsetY: int = ...,
        graphicType: Incomplete | None = ...,
        imageData: Incomplete | None = ...,
        rawdata: Incomplete | None = ...,
        gid: int = ...,
    ) -> None: ...
    def decompile(self, ttFont) -> None: ...
    def compile(self, ttFont) -> None: ...
    def toXML(self, xmlWriter, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
