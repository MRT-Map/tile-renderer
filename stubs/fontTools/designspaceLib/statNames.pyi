from typing import Dict, Optional

from _typeshed import Incomplete
from fontTools.designspaceLib import AxisDescriptor as AxisDescriptor
from fontTools.designspaceLib import AxisLabelDescriptor as AxisLabelDescriptor
from fontTools.designspaceLib import DesignSpaceDocument as DesignSpaceDocument
from fontTools.designspaceLib import (
    DesignSpaceDocumentError as DesignSpaceDocumentError,
)
from fontTools.designspaceLib import DiscreteAxisDescriptor as DiscreteAxisDescriptor
from fontTools.designspaceLib import SimpleLocationDict as SimpleLocationDict
from fontTools.designspaceLib import SourceDescriptor as SourceDescriptor

LOGGER: Incomplete
RibbiStyle = str
BOLD_ITALIC_TO_RIBBI_STYLE: Incomplete

class StatNames:
    familyNames: Dict[str, str]
    styleNames: Dict[str, str]
    postScriptFontName: Optional[str]
    styleMapFamilyNames: Dict[str, str]
    styleMapStyleName: Optional[RibbiStyle]
    def __init__(
        self,
        familyNames,
        styleNames,
        postScriptFontName,
        styleMapFamilyNames,
        styleMapStyleName,
    ) -> None: ...

def getStatNames(
    doc: DesignSpaceDocument, userLocation: SimpleLocationDict
) -> StatNames: ...
