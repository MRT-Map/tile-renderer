from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.ttLib.tables.TupleVariation import TupleVariation as TupleVariation
from fontTools.ttLib.tables.TupleVariation import (
    compileTupleVariationStore as compileTupleVariationStore,
)
from fontTools.ttLib.tables.TupleVariation import (
    decompileTupleVariationStore as decompileTupleVariationStore,
)

from . import DefaultTable as DefaultTable

CVAR_HEADER_FORMAT: str
CVAR_HEADER_SIZE: Incomplete

class table__c_v_a_r(DefaultTable.DefaultTable):
    dependencies: Incomplete
    variations: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    def compile(self, ttFont, useSharedPoints: bool = ...): ...
    majorVersion: Incomplete
    minorVersion: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def toXML(self, writer, ttFont) -> None: ...
