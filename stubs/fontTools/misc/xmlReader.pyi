from _typeshed import Incomplete
from fontTools import ttLib as ttLib
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.ttLib.tables.DefaultTable import DefaultTable as DefaultTable

log: Incomplete

class TTXParseError(Exception): ...

BUFSIZE: int

class XMLReader:
    file: Incomplete
    ttFont: Incomplete
    progress: Incomplete
    quiet: Incomplete
    root: Incomplete
    contentStack: Incomplete
    contentOnly: Incomplete
    stackSize: int
    def __init__(
        self,
        fileOrPath,
        ttFont,
        progress: Incomplete | None = ...,
        quiet: Incomplete | None = ...,
        contentOnly: bool = ...,
    ) -> None: ...
    def read(self, rootless: bool = ...) -> None: ...
    def close(self) -> None: ...

class ProgressPrinter:
    def __init__(self, title, maxval: int = ...) -> None: ...
    def set(self, val, maxval: Incomplete | None = ...) -> None: ...
    def increment(self, val: int = ...) -> None: ...
    def setLabel(self, text) -> None: ...
