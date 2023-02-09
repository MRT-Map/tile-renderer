from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytechr as bytechr
from fontTools.misc.textTools import byteord as byteord
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import deHexStr as deHexStr
from fontTools.misc.textTools import hexStr as hexStr
from fontTools.misc.textTools import readHex as readHex
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.textTools import strjoin as strjoin

from . import DefaultTable as DefaultTable
from .BitmapGlyphMetrics import BigGlyphMetrics as BigGlyphMetrics
from .BitmapGlyphMetrics import SmallGlyphMetrics as SmallGlyphMetrics
from .BitmapGlyphMetrics import bigGlyphMetricsFormat as bigGlyphMetricsFormat
from .BitmapGlyphMetrics import smallGlyphMetricsFormat as smallGlyphMetricsFormat

log: Incomplete
ebdtTableVersionFormat: str
ebdtComponentFormat: str

class table_E_B_D_T_(DefaultTable.DefaultTable):
    locatorName: str
    def getImageFormatClass(self, imageFormat): ...
    strikeData: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    version: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class EbdtComponent:
    def toXML(self, writer, ttFont) -> None: ...
    name: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class BitmapGlyph:
    fileExtension: str
    xmlDataFunctions: Incomplete
    data: Incomplete
    ttFont: Incomplete
    def __init__(self, data, ttFont) -> None: ...
    def __getattr__(self, attr): ...
    def ensureDecompiled(self, recurse: bool = ...) -> None: ...
    def getFormat(self): ...
    def toXML(self, strikeIndex, glyphName, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def writeMetrics(self, writer, ttFont) -> None: ...
    def readMetrics(self, name, attrs, content, ttFont) -> None: ...
    def writeData(self, strikeIndex, glyphName, writer, ttFont) -> None: ...
    def readData(self, name, attrs, content, ttFont) -> None: ...

BitmapPlusBigMetricsMixin: Incomplete
BitmapPlusSmallMetricsMixin: Incomplete

class BitAlignedBitmapMixin:
    def getRow(
        self,
        row,
        bitDepth: int = ...,
        metrics: Incomplete | None = ...,
        reverseBytes: bool = ...,
    ): ...
    imageData: Incomplete
    def setRows(
        self,
        dataRows,
        bitDepth: int = ...,
        metrics: Incomplete | None = ...,
        reverseBytes: bool = ...,
    ) -> None: ...

class ByteAlignedBitmapMixin:
    def getRow(
        self,
        row,
        bitDepth: int = ...,
        metrics: Incomplete | None = ...,
        reverseBytes: bool = ...,
    ): ...
    imageData: Incomplete
    def setRows(
        self,
        dataRows,
        bitDepth: int = ...,
        metrics: Incomplete | None = ...,
        reverseBytes: bool = ...,
    ) -> None: ...

class ebdt_bitmap_format_1(
    ByteAlignedBitmapMixin, BitmapPlusSmallMetricsMixin, BitmapGlyph
):
    metrics: Incomplete
    imageData: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

class ebdt_bitmap_format_2(
    BitAlignedBitmapMixin, BitmapPlusSmallMetricsMixin, BitmapGlyph
):
    metrics: Incomplete
    imageData: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

class ebdt_bitmap_format_5(BitAlignedBitmapMixin, BitmapGlyph):
    imageData: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

class ebdt_bitmap_format_6(
    ByteAlignedBitmapMixin, BitmapPlusBigMetricsMixin, BitmapGlyph
):
    metrics: Incomplete
    imageData: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

class ebdt_bitmap_format_7(
    BitAlignedBitmapMixin, BitmapPlusBigMetricsMixin, BitmapGlyph
):
    metrics: Incomplete
    imageData: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

class ComponentBitmapGlyph(BitmapGlyph):
    def toXML(self, strikeIndex, glyphName, writer, ttFont) -> None: ...
    componentArray: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class ebdt_bitmap_format_8(BitmapPlusSmallMetricsMixin, ComponentBitmapGlyph):
    metrics: Incomplete
    componentArray: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

class ebdt_bitmap_format_9(BitmapPlusBigMetricsMixin, ComponentBitmapGlyph):
    metrics: Incomplete
    componentArray: Incomplete
    def decompile(self) -> None: ...
    def compile(self, ttFont): ...

ebdt_bitmap_classes: Incomplete
