from _typeshed import Incomplete

from . import lib as lib
from .errors import UnsupportedGEOSVersionError as UnsupportedGEOSVersionError

class requires_geos:
    version: Incomplete
    def __init__(self, version) -> None: ...
    def __call__(self, func): ...

def multithreading_enabled(func): ...
