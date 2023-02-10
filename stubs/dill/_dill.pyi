from pickle import DEFAULT_PROTOCOL as DEFAULT_PROTOCOL
from pickle import HIGHEST_PROTOCOL as HIGHEST_PROTOCOL
from pickle import PickleError as PickleError
from pickle import PicklingError as PicklingError
from pickle import Unpickler as StockUnpickler
from pickle import UnpicklingError as UnpicklingError
from pickle import _Pickler as StockPickler

from _typeshed import Incomplete

BufferType = memoryview
ClassType = type
SliceType = slice
TypeType = type
XRangeType = range
IS_IPYTHON = __IPYTHON__  # type: ignore

class Sentinel:
    name: Incomplete
    __module__: Incomplete
    def __init__(self, name, module_name: Incomplete | None = ...) -> None: ...
    def __copy__(self): ...
    def __deepcopy__(self, memo): ...
    def __reduce__(self): ...
    def __reduce_ex__(self, protocol): ...

HANDLE_FMODE: int
CONTENTS_FMODE: int
FILE_FMODE: int

def copy(obj, *args, **kwds): ...
def dump(
    obj,
    file,
    protocol: Incomplete | None = ...,
    byref: Incomplete | None = ...,
    fmode: Incomplete | None = ...,
    recurse: Incomplete | None = ...,
    **kwds
) -> None: ...
def dumps(
    obj,
    protocol: Incomplete | None = ...,
    byref: Incomplete | None = ...,
    fmode: Incomplete | None = ...,
    recurse: Incomplete | None = ...,
    **kwds
): ...
def load(file, ignore: Incomplete | None = ..., **kwds): ...
def loads(str, ignore: Incomplete | None = ..., **kwds): ...

class MetaCatchingDict(dict):
    def get(self, key, default: Incomplete | None = ...): ...
    def __missing__(self, key): ...

class PickleWarning(Warning, PickleError): ...
class PicklingWarning(PickleWarning, PicklingError): ...
class UnpicklingWarning(PickleWarning, UnpicklingError): ...

class Pickler(StockPickler):
    dispatch: Incomplete  # type: ignore
    def __init__(self, file, *args, **kwds) -> None: ...
    def save(self, obj, save_persistent_id: bool = ...) -> None: ...
    def dump(self, obj) -> None: ...

class Unpickler(StockUnpickler):
    def find_class(self, module, name): ...
    def __init__(self, *args, **kwds) -> None: ...
    def load(self): ...

def pickle(t, func) -> None: ...
def register(t): ...

class match:
    value: Incomplete
    def __init__(self, value) -> None: ...
    def __enter__(self): ...
    def __exit__(self, *exc_info): ...
    args: Incomplete
    def case(self, args): ...
    @property
    def fields(self): ...
    def __getattr__(self, item): ...

CODE_VERSION = version  # type: ignore

class _itemgetter_helper:
    items: Incomplete
    def __init__(self) -> None: ...
    def __getitem__(self, item) -> None: ...

class _attrgetter_helper:
    attrs: Incomplete
    index: Incomplete
    def __init__(self, attrs, index: Incomplete | None = ...) -> None: ...
    def __getattribute__(self, attr): ...

class _dictproxy_helper(dict):
    def __ror__(self, a): ...

def pickles(obj, exact: bool = ..., safe: bool = ..., **kwds): ...
def check(obj, *args, **kwds) -> None: ...
