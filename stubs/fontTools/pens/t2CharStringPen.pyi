from _typeshed import Incomplete
from fontTools.cffLib.specializer import commandsToProgram as commandsToProgram
from fontTools.cffLib.specializer import specializeCommands as specializeCommands
from fontTools.misc.psCharStrings import T2CharString as T2CharString
from fontTools.misc.roundTools import otRound as otRound
from fontTools.misc.roundTools import roundFunc as roundFunc
from fontTools.pens.basePen import BasePen as BasePen

class T2CharStringPen(BasePen):
    round: Incomplete
    def __init__(
        self, width, glyphSet, roundTolerance: float = ..., CFF2: bool = ...
    ) -> None: ...
    def getCharString(
        self,
        private: Incomplete | None = ...,
        globalSubrs: Incomplete | None = ...,
        optimize: bool = ...,
    ): ...
