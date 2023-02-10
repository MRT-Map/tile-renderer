from collections.abc import Sequence

from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.textTools import strjoin as strjoin
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.textTools import tostr as tostr

from . import DefaultTable as DefaultTable

log: Incomplete
SVG_format_0: str
SVG_format_0Size: Incomplete
doc_index_entry_format_0: str
doc_index_entry_format_0Size: Incomplete

class table_S_V_G_(DefaultTable.DefaultTable):
    docList: Incomplete
    numEntries: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class DocumentIndexEntry:
    startGlyphID: Incomplete
    endGlyphID: Incomplete
    svgDocOffset: Incomplete
    svgDocLength: Incomplete
    def __init__(self) -> None: ...

class SVGDocument(Sequence):
    data: str
    startGlyphID: int
    endGlyphID: int
    compressed: bool
    def __getitem__(self, index): ...
    def __len__(self) -> int: ...
    def __init__(self, data, startGlyphID, endGlyphID, compressed) -> None: ...
