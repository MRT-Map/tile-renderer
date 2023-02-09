from typing import Dict, List, Optional, Tuple, Union

from _typeshed import Incomplete
from fontTools.misc import etree as ET
from fontTools.misc.loggingTools import LogMixin

class DesignSpaceDocumentError(Exception):
    msg: Incomplete
    obj: Incomplete
    def __init__(self, msg, obj: Incomplete | None = ...) -> None: ...

class AsDictMixin:
    def asdict(self): ...

class SimpleDescriptor(AsDictMixin):
    def compare(self, other) -> None: ...

class SourceDescriptor(SimpleDescriptor):
    flavor: str
    filename: Incomplete
    path: Incomplete
    font: Incomplete
    name: Incomplete
    designLocation: Incomplete
    layerName: Incomplete
    familyName: Incomplete
    styleName: Incomplete
    localisedFamilyName: Incomplete
    copyLib: Incomplete
    copyInfo: Incomplete
    copyGroups: Incomplete
    copyFeatures: Incomplete
    muteKerning: Incomplete
    muteInfo: Incomplete
    mutedGlyphNames: Incomplete
    def __init__(
        self,
        *,
        filename: Incomplete | None = ...,
        path: Incomplete | None = ...,
        font: Incomplete | None = ...,
        name: Incomplete | None = ...,
        location: Incomplete | None = ...,
        designLocation: Incomplete | None = ...,
        layerName: Incomplete | None = ...,
        familyName: Incomplete | None = ...,
        styleName: Incomplete | None = ...,
        localisedFamilyName: Incomplete | None = ...,
        copyLib: bool = ...,
        copyInfo: bool = ...,
        copyGroups: bool = ...,
        copyFeatures: bool = ...,
        muteKerning: bool = ...,
        muteInfo: bool = ...,
        mutedGlyphNames: Incomplete | None = ...
    ) -> None: ...
    @property
    def location(self): ...
    @location.setter
    def location(self, location: Optional[AnisotropicLocationDict]): ...
    def setFamilyName(self, familyName, languageCode: str = ...) -> None: ...
    def getFamilyName(self, languageCode: str = ...): ...
    def getFullDesignLocation(
        self, doc: DesignSpaceDocument
    ) -> AnisotropicLocationDict: ...

class RuleDescriptor(SimpleDescriptor):
    name: Incomplete
    conditionSets: Incomplete
    subs: Incomplete
    def __init__(
        self,
        *,
        name: Incomplete | None = ...,
        conditionSets: Incomplete | None = ...,
        subs: Incomplete | None = ...
    ) -> None: ...

AnisotropicLocationDict = Dict[str, Union[float, Tuple[float, float]]]
SimpleLocationDict = Dict[str, float]

class InstanceDescriptor(SimpleDescriptor):
    flavor: str
    filename: Incomplete
    path: Incomplete
    font: Incomplete
    name: Incomplete
    locationLabel: Incomplete
    designLocation: Incomplete
    userLocation: Incomplete
    familyName: Incomplete
    styleName: Incomplete
    postScriptFontName: Incomplete
    styleMapFamilyName: Incomplete
    styleMapStyleName: Incomplete
    localisedFamilyName: Incomplete
    localisedStyleName: Incomplete
    localisedStyleMapFamilyName: Incomplete
    localisedStyleMapStyleName: Incomplete
    glyphs: Incomplete
    kerning: Incomplete
    info: Incomplete
    lib: Incomplete
    def __init__(
        self,
        *,
        filename: Incomplete | None = ...,
        path: Incomplete | None = ...,
        font: Incomplete | None = ...,
        name: Incomplete | None = ...,
        location: Incomplete | None = ...,
        locationLabel: Incomplete | None = ...,
        designLocation: Incomplete | None = ...,
        userLocation: Incomplete | None = ...,
        familyName: Incomplete | None = ...,
        styleName: Incomplete | None = ...,
        postScriptFontName: Incomplete | None = ...,
        styleMapFamilyName: Incomplete | None = ...,
        styleMapStyleName: Incomplete | None = ...,
        localisedFamilyName: Incomplete | None = ...,
        localisedStyleName: Incomplete | None = ...,
        localisedStyleMapFamilyName: Incomplete | None = ...,
        localisedStyleMapStyleName: Incomplete | None = ...,
        glyphs: Incomplete | None = ...,
        kerning: bool = ...,
        info: bool = ...,
        lib: Incomplete | None = ...
    ) -> None: ...
    @property
    def location(self): ...
    @location.setter
    def location(self, location: Optional[AnisotropicLocationDict]): ...
    def setStyleName(self, styleName, languageCode: str = ...) -> None: ...
    def getStyleName(self, languageCode: str = ...): ...
    def setFamilyName(self, familyName, languageCode: str = ...) -> None: ...
    def getFamilyName(self, languageCode: str = ...): ...
    def setStyleMapStyleName(
        self, styleMapStyleName, languageCode: str = ...
    ) -> None: ...
    def getStyleMapStyleName(self, languageCode: str = ...): ...
    def setStyleMapFamilyName(
        self, styleMapFamilyName, languageCode: str = ...
    ) -> None: ...
    def getStyleMapFamilyName(self, languageCode: str = ...): ...
    def clearLocation(self, axisName: Optional[str] = ...): ...
    def getLocationLabelDescriptor(
        self, doc: DesignSpaceDocument
    ) -> Optional[LocationLabelDescriptor]: ...
    def getFullDesignLocation(
        self, doc: DesignSpaceDocument
    ) -> AnisotropicLocationDict: ...
    def getFullUserLocation(self, doc: DesignSpaceDocument) -> SimpleLocationDict: ...

class AbstractAxisDescriptor(SimpleDescriptor):
    flavor: str
    tag: Incomplete
    name: Incomplete
    labelNames: Incomplete
    hidden: Incomplete
    map: Incomplete
    axisOrdering: Incomplete
    axisLabels: Incomplete
    def __init__(
        self,
        *,
        tag: Incomplete | None = ...,
        name: Incomplete | None = ...,
        labelNames: Incomplete | None = ...,
        hidden: bool = ...,
        map: Incomplete | None = ...,
        axisOrdering: Incomplete | None = ...,
        axisLabels: Incomplete | None = ...
    ) -> None: ...

class AxisDescriptor(AbstractAxisDescriptor):
    minimum: Incomplete
    maximum: Incomplete
    default: Incomplete
    def __init__(
        self,
        *,
        tag: Incomplete | None = ...,
        name: Incomplete | None = ...,
        labelNames: Incomplete | None = ...,
        minimum: Incomplete | None = ...,
        default: Incomplete | None = ...,
        maximum: Incomplete | None = ...,
        hidden: bool = ...,
        map: Incomplete | None = ...,
        axisOrdering: Incomplete | None = ...,
        axisLabels: Incomplete | None = ...
    ) -> None: ...
    def serialize(self): ...
    def map_forward(self, v): ...
    def map_backward(self, v): ...

class DiscreteAxisDescriptor(AbstractAxisDescriptor):
    flavor: str
    default: Incomplete
    values: Incomplete
    def __init__(
        self,
        *,
        tag: Incomplete | None = ...,
        name: Incomplete | None = ...,
        labelNames: Incomplete | None = ...,
        values: Incomplete | None = ...,
        default: Incomplete | None = ...,
        hidden: bool = ...,
        map: Incomplete | None = ...,
        axisOrdering: Incomplete | None = ...,
        axisLabels: Incomplete | None = ...
    ) -> None: ...
    def map_forward(self, value): ...
    def map_backward(self, value): ...

class AxisLabelDescriptor(SimpleDescriptor):
    flavor: str
    userMinimum: Incomplete
    userValue: Incomplete
    userMaximum: Incomplete
    name: Incomplete
    elidable: Incomplete
    olderSibling: Incomplete
    linkedUserValue: Incomplete
    labelNames: Incomplete
    def __init__(
        self,
        *,
        name,
        userValue,
        userMinimum: Incomplete | None = ...,
        userMaximum: Incomplete | None = ...,
        elidable: bool = ...,
        olderSibling: bool = ...,
        linkedUserValue: Incomplete | None = ...,
        labelNames: Incomplete | None = ...
    ) -> None: ...
    def getFormat(self) -> int: ...
    @property
    def defaultName(self) -> str: ...

class LocationLabelDescriptor(SimpleDescriptor):
    flavor: str
    name: Incomplete
    userLocation: Incomplete
    elidable: Incomplete
    olderSibling: Incomplete
    labelNames: Incomplete
    def __init__(
        self,
        *,
        name,
        userLocation,
        elidable: bool = ...,
        olderSibling: bool = ...,
        labelNames: Incomplete | None = ...
    ) -> None: ...
    @property
    def defaultName(self) -> str: ...
    def getFullUserLocation(self, doc: DesignSpaceDocument) -> SimpleLocationDict: ...

class VariableFontDescriptor(SimpleDescriptor):
    flavor: str
    filename: Incomplete
    name: Incomplete
    axisSubsets: Incomplete
    lib: Incomplete
    def __init__(
        self,
        *,
        name,
        filename: Incomplete | None = ...,
        axisSubsets: Incomplete | None = ...,
        lib: Incomplete | None = ...
    ) -> None: ...

class RangeAxisSubsetDescriptor(SimpleDescriptor):
    flavor: str
    name: Incomplete
    userMinimum: Incomplete
    userDefault: Incomplete
    userMaximum: Incomplete
    def __init__(
        self,
        *,
        name,
        userMinimum=...,
        userDefault: Incomplete | None = ...,
        userMaximum=...
    ) -> None: ...

class ValueAxisSubsetDescriptor(SimpleDescriptor):
    flavor: str
    name: Incomplete
    userValue: Incomplete
    def __init__(self, *, name, userValue) -> None: ...

class BaseDocWriter:
    axisDescriptorClass: Incomplete
    discreteAxisDescriptorClass: Incomplete
    axisLabelDescriptorClass: Incomplete
    locationLabelDescriptorClass: Incomplete
    ruleDescriptorClass: Incomplete
    sourceDescriptorClass: Incomplete
    variableFontDescriptorClass: Incomplete
    valueAxisSubsetDescriptorClass: Incomplete
    rangeAxisSubsetDescriptorClass: Incomplete
    instanceDescriptorClass: Incomplete
    @classmethod
    def getAxisDecriptor(cls): ...
    @classmethod
    def getSourceDescriptor(cls): ...
    @classmethod
    def getInstanceDescriptor(cls): ...
    @classmethod
    def getRuleDescriptor(cls): ...
    path: Incomplete
    documentObject: Incomplete
    effectiveFormatTuple: Incomplete
    root: Incomplete
    def __init__(self, documentPath, documentObject: DesignSpaceDocument) -> None: ...
    def write(
        self, pretty: bool = ..., encoding: str = ..., xml_declaration: bool = ...
    ) -> None: ...
    def intOrFloat(self, num): ...

class BaseDocReader(LogMixin):
    axisDescriptorClass: Incomplete
    discreteAxisDescriptorClass: Incomplete
    axisLabelDescriptorClass: Incomplete
    locationLabelDescriptorClass: Incomplete
    ruleDescriptorClass: Incomplete
    sourceDescriptorClass: Incomplete
    variableFontsDescriptorClass: Incomplete
    valueAxisSubsetDescriptorClass: Incomplete
    rangeAxisSubsetDescriptorClass: Incomplete
    instanceDescriptorClass: Incomplete
    path: Incomplete
    documentObject: Incomplete
    root: Incomplete
    rules: Incomplete
    sources: Incomplete
    instances: Incomplete
    axisDefaults: Incomplete
    def __init__(self, documentPath, documentObject) -> None: ...
    @classmethod
    def fromstring(cls, string, documentObject): ...
    def read(self) -> None: ...
    def readRules(self) -> None: ...
    def readAxes(self) -> None: ...
    def readAxisLabel(self, element: ET.Element): ...
    def readLabels(self) -> None: ...
    def readVariableFonts(self) -> None: ...
    def readAxisSubset(self, element: ET.Element): ...
    def readSources(self) -> None: ...
    def locationFromElement(self, element): ...
    def readLocationElement(self, locationElement): ...
    def readInstances(
        self, makeGlyphs: bool = ..., makeKerning: bool = ..., makeInfo: bool = ...
    ) -> None: ...
    def readLibElement(self, libElement, instanceObject) -> None: ...
    def readInfoElement(self, infoElement, instanceObject) -> None: ...
    def readGlyphElement(self, glyphElement, instanceObject) -> None: ...
    def readLib(self) -> None: ...

class DesignSpaceDocument(LogMixin, AsDictMixin):
    path: Incomplete
    filename: Incomplete
    formatVersion: Incomplete
    elidedFallbackName: Incomplete
    axes: Incomplete
    locationLabels: Incomplete
    rules: Incomplete
    rulesProcessingLast: bool
    sources: Incomplete
    variableFonts: Incomplete
    instances: Incomplete
    lib: Incomplete
    default: Incomplete
    readerClass: Incomplete
    writerClass: Incomplete
    def __init__(
        self, readerClass: Incomplete | None = ..., writerClass: Incomplete | None = ...
    ) -> None: ...
    @classmethod
    def fromfile(
        cls,
        path,
        readerClass: Incomplete | None = ...,
        writerClass: Incomplete | None = ...,
    ): ...
    @classmethod
    def fromstring(
        cls,
        string,
        readerClass: Incomplete | None = ...,
        writerClass: Incomplete | None = ...,
    ): ...
    def tostring(self, encoding: Incomplete | None = ...): ...
    def read(self, path) -> None: ...
    def write(self, path) -> None: ...
    def updatePaths(self) -> None: ...
    def addSource(self, sourceDescriptor: SourceDescriptor): ...
    def addSourceDescriptor(self, **kwargs): ...
    def addInstance(self, instanceDescriptor: InstanceDescriptor): ...
    def addInstanceDescriptor(self, **kwargs): ...
    def addAxis(
        self, axisDescriptor: Union[AxisDescriptor, DiscreteAxisDescriptor]
    ): ...
    def addAxisDescriptor(self, **kwargs): ...
    def addRule(self, ruleDescriptor: RuleDescriptor): ...
    def addRuleDescriptor(self, **kwargs): ...
    def addVariableFont(self, variableFontDescriptor: VariableFontDescriptor): ...
    def addVariableFontDescriptor(self, **kwargs): ...
    def addLocationLabel(self, locationLabelDescriptor: LocationLabelDescriptor): ...
    def addLocationLabelDescriptor(self, **kwargs): ...
    def newDefaultLocation(self): ...
    def labelForUserLocation(
        self, userLocation: SimpleLocationDict
    ) -> Optional[LocationLabelDescriptor]: ...
    def updateFilenameFromPath(
        self, masters: bool = ..., instances: bool = ..., force: bool = ...
    ) -> None: ...
    def newAxisDescriptor(self): ...
    def newSourceDescriptor(self): ...
    def newInstanceDescriptor(self): ...
    def getAxisOrder(self): ...
    def getAxis(self, name): ...
    def getLocationLabel(self, name: str) -> Optional[LocationLabelDescriptor]: ...
    def map_forward(self, userLocation: SimpleLocationDict) -> SimpleLocationDict: ...
    def map_backward(
        self, designLocation: AnisotropicLocationDict
    ) -> SimpleLocationDict: ...
    def findDefault(self): ...
    def normalizeLocation(self, location): ...
    def normalize(self) -> None: ...
    def loadSourceFonts(self, opener, **kwargs): ...
    @property
    def formatTuple(self): ...
    def getVariableFonts(self) -> List[VariableFontDescriptor]: ...
    def deepcopyExceptFonts(self): ...
