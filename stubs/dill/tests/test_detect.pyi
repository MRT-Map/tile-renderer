from pickle import PicklingError as PicklingError

from _typeshed import Incomplete
from dill import settings as settings
from dill._dill import IS_PYPY as IS_PYPY
from dill.detect import at as at
from dill.detect import baditems as baditems
from dill.detect import badobjects as badobjects
from dill.detect import badtypes as badtypes
from dill.detect import errors as errors
from dill.detect import globalvars as globalvars
from dill.detect import parent as parent

def test_bad_things() -> None: ...
def test_parent() -> None: ...

a: Incomplete
b: Incomplete
c: Incomplete

def squared(x): ...
def foo(x): ...

class _class:
    def ok(self): ...

def test_globals() -> None: ...

bar: Incomplete

class Foo:
    def __init__(self) -> None: ...

f: Incomplete

def test_getstate(): ...
def test_deleted(): ...
def test_lambdify() -> None: ...
