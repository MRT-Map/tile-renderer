from _typeshed import Incomplete

class _UnicodeCustom:
    codes: Incomplete
    def __init__(self, f) -> None: ...
    def __getitem__(self, charCode): ...

class _UnicodeBuiltin:
    def __getitem__(self, charCode): ...

Unicode: Incomplete

def setUnicodeData(f) -> None: ...
