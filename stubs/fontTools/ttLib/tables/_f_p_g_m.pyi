from _typeshed import Incomplete

from . import DefaultTable as DefaultTable
from . import ttProgram as ttProgram

class table__f_p_g_m(DefaultTable.DefaultTable):
    program: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def __bool__(self) -> bool: ...
    __nonzero__: Incomplete
