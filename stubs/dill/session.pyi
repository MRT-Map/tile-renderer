from typing import Optional, Union

from _typeshed import Incomplete

from ._dill import ModuleType  # type: ignore

def dump_module(
    filename=...,
    module: Optional[Union[ModuleType, str]] = ...,
    refimported: bool = ...,
    **kwds
) -> None: ...
def dump_session(
    filename=..., main: Incomplete | None = ..., byref: bool = ..., **kwds
) -> None: ...

class _PeekableReader:
    stream: Incomplete
    def __init__(self, stream) -> None: ...
    def read(self, n): ...
    def readline(self): ...
    def tell(self): ...
    def close(self): ...
    def peek(self, n): ...

def load_module(
    filename=..., module: Optional[Union[ModuleType, str]] = ..., **kwds
) -> Optional[ModuleType]: ...
def load_session(filename=..., main: Incomplete | None = ..., **kwds) -> None: ...
def load_module_asdict(filename=..., update: bool = ..., **kwds) -> dict: ...