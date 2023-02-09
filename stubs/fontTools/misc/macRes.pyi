from collections.abc import MutableMapping

from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import tostr as tostr

class ResourceError(Exception): ...

class ResourceReader(MutableMapping):
    file: Incomplete
    def __init__(self, fileOrPath) -> None: ...
    @staticmethod
    def openResourceFork(path): ...
    @staticmethod
    def openDataFork(path): ...
    def __getitem__(self, resType): ...
    def __delitem__(self, resType) -> None: ...
    def __setitem__(self, resType, resources) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self): ...
    def keys(self): ...
    @property
    def types(self): ...
    def countResources(self, resType): ...
    def getIndices(self, resType): ...
    def getNames(self, resType): ...
    def getIndResource(self, resType, index): ...
    def getNamedResource(self, resType, name): ...
    def close(self) -> None: ...

class Resource:
    type: Incomplete
    data: Incomplete
    id: Incomplete
    name: Incomplete
    attr: Incomplete
    def __init__(
        self,
        resType: Incomplete | None = ...,
        resData: Incomplete | None = ...,
        resID: Incomplete | None = ...,
        resName: Incomplete | None = ...,
        resAttr: Incomplete | None = ...,
    ) -> None: ...
    def decompile(self, refData, reader) -> None: ...

ResourceForkHeader: str
ResourceForkHeaderSize: Incomplete
ResourceMapHeader: str
ResourceMapHeaderSize: Incomplete
ResourceTypeItem: str
ResourceTypeItemSize: Incomplete
ResourceRefItem: str
ResourceRefItemSize: Incomplete