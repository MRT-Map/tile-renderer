from _typeshed import Incomplete
from fontTools.merge.unicode import is_Default_Ignorable as is_Default_Ignorable
from fontTools.pens.recordingPen import (
    DecomposingRecordingPen as DecomposingRecordingPen,
)

log: Incomplete

def computeMegaGlyphOrder(merger, glyphOrders) -> None: ...

class _CmapUnicodePlatEncodings:
    BMP: Incomplete
    FullRepertoire: Incomplete

def computeMegaCmap(merger, cmapTables) -> None: ...
def renameCFFCharStrings(merger, glyphOrder, cffTable) -> None: ...
