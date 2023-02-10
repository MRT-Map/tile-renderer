from _typeshed import Incomplete
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

GASP_SYMMETRIC_GRIDFIT: int
GASP_SYMMETRIC_SMOOTHING: int
GASP_DOGRAY: int
GASP_GRIDFIT: int

class table__g_a_s_p(DefaultTable.DefaultTable):
    gaspRange: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
