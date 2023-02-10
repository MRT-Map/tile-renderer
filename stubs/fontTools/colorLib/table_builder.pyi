import enum

from _typeshed import Incomplete
from fontTools.misc.roundTools import otRound as otRound
from fontTools.ttLib.tables.otBase import BaseTable as BaseTable
from fontTools.ttLib.tables.otBase import (
    FormatSwitchingBaseTable as FormatSwitchingBaseTable,
)
from fontTools.ttLib.tables.otBase import (
    UInt8FormatSwitchingBaseTable as UInt8FormatSwitchingBaseTable,
)
from fontTools.ttLib.tables.otConverters import ComputedInt as ComputedInt
from fontTools.ttLib.tables.otConverters import FloatValue as FloatValue
from fontTools.ttLib.tables.otConverters import IntValue as IntValue
from fontTools.ttLib.tables.otConverters import OptionalValue as OptionalValue
from fontTools.ttLib.tables.otConverters import Short as Short
from fontTools.ttLib.tables.otConverters import SimpleValue as SimpleValue
from fontTools.ttLib.tables.otConverters import Struct as Struct
from fontTools.ttLib.tables.otConverters import UInt8 as UInt8
from fontTools.ttLib.tables.otConverters import UShort as UShort

class BuildCallback(enum.Enum):
    BEFORE_BUILD: Incomplete
    AFTER_BUILD: Incomplete
    CREATE_DEFAULT: Incomplete

class TableBuilder:
    def __init__(self, callbackTable: Incomplete | None = ...) -> None: ...
    def build(self, cls, source): ...

class TableUnbuilder:
    def __init__(self, callbackTable: Incomplete | None = ...) -> None: ...
    def unbuild(self, table): ...
