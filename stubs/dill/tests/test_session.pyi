from calendar import Calendar
from calendar import isleap as isleap
from xml import sax as sax

import __main__
from _typeshed import Incomplete

session_file: Incomplete
refimported: Incomplete

def test_modules(refimported) -> None: ...

x: int
empty: Incomplete
names: Incomplete

def squared(x): ...

cubed: Incomplete

class Person:
    name: Incomplete
    age: Incomplete
    def __init__(self, name, age) -> None: ...

person: Incomplete

class CalendarSubclass(Calendar):
    def weekdays(self): ...

cal: Incomplete
selfref = __main__

class TestNamespace:
    test_globals: Incomplete
    extra: Incomplete
    def __init__(self, **extra) -> None: ...
    backup: Incomplete
    def __enter__(self): ...
    def __exit__(self, *exc_info) -> None: ...

def test_session_main(refimported) -> None: ...
def test_session_other() -> None: ...
def test_runtime_module() -> None: ...
def test_refimported_imported_as() -> None: ...
def test_load_module_asdict() -> None: ...
