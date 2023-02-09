from _typeshed import Incomplete
from fontTools.ttLib.sfnt import readTTCHeader as readTTCHeader
from fontTools.ttLib.sfnt import writeTTCHeader as writeTTCHeader
from fontTools.ttLib.ttFont import TTFont as TTFont

log: Incomplete

class TTCollection:
    def __init__(
        self, file: Incomplete | None = ..., shareTables: bool = ..., **kwargs
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(self, type, value, traceback) -> None: ...
    def close(self) -> None: ...
    def save(self, file, shareTables: bool = ...) -> None: ...
    def saveXML(
        self, fileOrPath, newlinestr: str = ..., writeVersion: bool = ..., **kwargs
    ) -> None: ...
    def __getitem__(self, item): ...
    def __setitem__(self, item, value) -> None: ...
    def __delitem__(self, item): ...
    def __len__(self) -> int: ...
    def __iter__(self): ...
