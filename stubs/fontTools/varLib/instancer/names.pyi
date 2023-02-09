from collections.abc import Generator
from copy import deepcopy as deepcopy
from enum import IntEnum

class NameID(IntEnum):
    FAMILY_NAME: int
    SUBFAMILY_NAME: int
    UNIQUE_FONT_IDENTIFIER: int
    FULL_FONT_NAME: int
    VERSION_STRING: int
    POSTSCRIPT_NAME: int
    TYPOGRAPHIC_FAMILY_NAME: int
    TYPOGRAPHIC_SUBFAMILY_NAME: int
    VARIATIONS_POSTSCRIPT_NAME_PREFIX: int

ELIDABLE_AXIS_VALUE_NAME: int

def getVariationNameIDs(varfont): ...
def pruningUnusedNames(varfont) -> Generator[None, None, None]: ...
def updateNameTable(varfont, axisLimits) -> None: ...
def checkAxisValuesExist(stat, axisValues, axisCoords) -> None: ...
