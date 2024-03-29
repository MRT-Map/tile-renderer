from _typeshed import Incomplete
from fontTools.misc.textTools import readHex as readHex
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.ttLib import getSearchRange as getSearchRange

from . import DefaultTable as DefaultTable

log: Incomplete

class table__k_e_r_n(DefaultTable.DefaultTable):
    def getkern(self, format): ...
    version: Incomplete
    kernTables: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class KernTable_format_0:
    version: int
    format: int
    apple: Incomplete
    def __init__(self, apple: bool = ...) -> None: ...
    coverage: Incomplete
    tupleIndex: Incomplete
    kernTable: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def __getitem__(self, pair): ...
    def __setitem__(self, pair, value) -> None: ...
    def __delitem__(self, pair) -> None: ...

class KernTable_format_unkown:
    format: Incomplete
    def __init__(self, format) -> None: ...
    data: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

kern_classes: Incomplete
