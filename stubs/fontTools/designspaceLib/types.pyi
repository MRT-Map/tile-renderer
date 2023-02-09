from typing import Dict, List, Optional, Union

from fontTools.designspaceLib import AxisDescriptor as AxisDescriptor
from fontTools.designspaceLib import DesignSpaceDocument as DesignSpaceDocument
from fontTools.designspaceLib import (
    DesignSpaceDocumentError as DesignSpaceDocumentError,
)
from fontTools.designspaceLib import (
    RangeAxisSubsetDescriptor as RangeAxisSubsetDescriptor,
)
from fontTools.designspaceLib import SimpleLocationDict as SimpleLocationDict
from fontTools.designspaceLib import (
    ValueAxisSubsetDescriptor as ValueAxisSubsetDescriptor,
)
from fontTools.designspaceLib import VariableFontDescriptor as VariableFontDescriptor

def clamp(value, minimum, maximum): ...

class Range:
    minimum: float
    maximum: float
    default: float
    def __post_init__(self) -> None: ...
    def __contains__(self, value: Union[float, Range]) -> bool: ...
    def intersection(self, other: Range) -> Optional[Range]: ...
    def __init__(self, minimum, maximum, default) -> None: ...

Region = Dict[str, Union[Range, float]]
ConditionSet = Dict[str, Range]
Rule = List[ConditionSet]
Rules = Dict[str, Rule]

def locationInRegion(location: SimpleLocationDict, region: Region) -> bool: ...
def regionInRegion(region: Region, superRegion: Region) -> bool: ...
def userRegionToDesignRegion(
    doc: DesignSpaceDocument, userRegion: Region
) -> Region: ...
def getVFUserRegion(doc: DesignSpaceDocument, vf: VariableFontDescriptor) -> Region: ...
