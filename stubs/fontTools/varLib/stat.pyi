from typing import Dict, List

from fontTools.designspaceLib import AxisLabelDescriptor as AxisLabelDescriptor
from fontTools.designspaceLib import DesignSpaceDocument as DesignSpaceDocument
from fontTools.designspaceLib import (
    DesignSpaceDocumentError as DesignSpaceDocumentError,
)
from fontTools.designspaceLib import LocationLabelDescriptor as LocationLabelDescriptor
from fontTools.designspaceLib.types import Region as Region
from fontTools.designspaceLib.types import getVFUserRegion as getVFUserRegion
from fontTools.designspaceLib.types import locationInRegion as locationInRegion
from fontTools.ttLib import TTFont as TTFont

def buildVFStatTable(ttFont: TTFont, doc: DesignSpaceDocument, vfName: str) -> None: ...
def getStatAxes(doc: DesignSpaceDocument, userRegion: Region) -> List[Dict]: ...
def getStatLocations(doc: DesignSpaceDocument, userRegion: Region) -> List[Dict]: ...
