from typing import Callable, Dict, Iterator, Tuple

from _typeshed import Incomplete
from fontTools.designspaceLib import AxisDescriptor as AxisDescriptor
from fontTools.designspaceLib import DesignSpaceDocument as DesignSpaceDocument
from fontTools.designspaceLib import DiscreteAxisDescriptor as DiscreteAxisDescriptor
from fontTools.designspaceLib import InstanceDescriptor as InstanceDescriptor
from fontTools.designspaceLib import RuleDescriptor as RuleDescriptor
from fontTools.designspaceLib import SimpleLocationDict as SimpleLocationDict
from fontTools.designspaceLib import SourceDescriptor as SourceDescriptor
from fontTools.designspaceLib import VariableFontDescriptor as VariableFontDescriptor
from fontTools.designspaceLib.statNames import StatNames as StatNames
from fontTools.designspaceLib.statNames import getStatNames as getStatNames
from fontTools.designspaceLib.types import ConditionSet as ConditionSet
from fontTools.designspaceLib.types import Range as Range
from fontTools.designspaceLib.types import Region as Region
from fontTools.designspaceLib.types import getVFUserRegion as getVFUserRegion
from fontTools.designspaceLib.types import locationInRegion as locationInRegion
from fontTools.designspaceLib.types import regionInRegion as regionInRegion
from fontTools.designspaceLib.types import (
    userRegionToDesignRegion as userRegionToDesignRegion,
)

LOGGER: Incomplete
MakeInstanceFilenameCallable = Callable[
    [DesignSpaceDocument, InstanceDescriptor, StatNames], str
]

def defaultMakeInstanceFilename(
    doc: DesignSpaceDocument, instance: InstanceDescriptor, statNames: StatNames
) -> str: ...
def splitInterpolable(
    doc: DesignSpaceDocument,
    makeNames: bool = ...,
    expandLocations: bool = ...,
    makeInstanceFilename: MakeInstanceFilenameCallable = ...,
) -> Iterator[Tuple[SimpleLocationDict, DesignSpaceDocument]]: ...
def splitVariableFonts(
    doc: DesignSpaceDocument,
    makeNames: bool = ...,
    expandLocations: bool = ...,
    makeInstanceFilename: MakeInstanceFilenameCallable = ...,
) -> Iterator[Tuple[str, DesignSpaceDocument]]: ...
def convert5to4(doc: DesignSpaceDocument) -> Dict[str, DesignSpaceDocument]: ...
