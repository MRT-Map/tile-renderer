from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

Gloc_header: str

class table_G__l_o_c(DefaultTable.DefaultTable):
    dependencies: Incomplete
    attribIds: Incomplete
    numAttribs: int
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    locations: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def set(self, locations) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def __getitem__(self, index): ...
    def __len__(self) -> int: ...
    def __iter__(self): ...
