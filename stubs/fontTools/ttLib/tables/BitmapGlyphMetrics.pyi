from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval

log: Incomplete
bigGlyphMetricsFormat: str
smallGlyphMetricsFormat: str

class BitmapGlyphMetrics:
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class BigGlyphMetrics(BitmapGlyphMetrics):
    binaryFormat: Incomplete

class SmallGlyphMetrics(BitmapGlyphMetrics):
    binaryFormat: Incomplete
