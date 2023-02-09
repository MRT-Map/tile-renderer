from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

vheaFormat: str

class table__v_h_e_a(DefaultTable.DefaultTable):
    dependencies: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    tableVersion: Incomplete
    def compile(self, ttFont): ...
    advanceHeightMax: Incomplete
    minTopSideBearing: Incomplete
    minBottomSideBearing: Incomplete
    yMaxExtent: Incomplete
    def recalc(self, ttFont) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    @property
    def reserved0(self): ...
    caretOffset: Incomplete
    @reserved0.setter
    def reserved0(self, value) -> None: ...
