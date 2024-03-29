from _typeshed import Incomplete

class FontBuilder:
    font: Incomplete
    isTTF: Incomplete
    def __init__(
        self,
        unitsPerEm: Incomplete | None = ...,
        font: Incomplete | None = ...,
        isTTF: bool = ...,
    ) -> None: ...
    def save(self, file) -> None: ...
    def setupHead(self, **values) -> None: ...
    def updateHead(self, **values) -> None: ...
    def setupGlyphOrder(self, glyphOrder) -> None: ...
    def setupCharacterMap(
        self, cmapping, uvs: Incomplete | None = ..., allowFallback: bool = ...
    ) -> None: ...
    def setupNameTable(
        self, nameStrings, windows: bool = ..., mac: bool = ...
    ) -> None: ...
    def setupOS2(self, **values) -> None: ...
    def setupCFF(self, psName, fontInfo, charStringsDict, privateDict) -> None: ...
    def setupCFF2(
        self,
        charStringsDict,
        fdArrayList: Incomplete | None = ...,
        regions: Incomplete | None = ...,
    ) -> None: ...
    def setupCFF2Regions(self, regions) -> None: ...
    def setupGlyf(self, glyphs, calcGlyphBounds: bool = ...) -> None: ...
    def setupFvar(self, axes, instances) -> None: ...
    def setupAvar(self, axes) -> None: ...
    def setupGvar(self, variations) -> None: ...
    def calcGlyphBounds(self) -> None: ...
    def setupHorizontalMetrics(self, metrics) -> None: ...
    def setupVerticalMetrics(self, metrics) -> None: ...
    def setupMetrics(self, tableTag, metrics) -> None: ...
    def setupHorizontalHeader(self, **values) -> None: ...
    def setupVerticalHeader(self, **values) -> None: ...
    def setupVerticalOrigins(
        self, verticalOrigins, defaultVerticalOrigin: Incomplete | None = ...
    ): ...
    def setupPost(self, keepGlyphNames: bool = ..., **values) -> None: ...
    def setupMaxp(self) -> None: ...
    def setupDummyDSIG(self) -> None: ...
    def addOpenTypeFeatures(
        self,
        features,
        filename: Incomplete | None = ...,
        tables: Incomplete | None = ...,
    ) -> None: ...
    def addFeatureVariations(
        self, conditionalSubstitutions, featureTag: str = ...
    ) -> None: ...
    def setupCOLR(
        self,
        colorLayers,
        version: Incomplete | None = ...,
        varStore: Incomplete | None = ...,
        varIndexMap: Incomplete | None = ...,
        clipBoxes: Incomplete | None = ...,
        allowLayerReuse: bool = ...,
    ) -> None: ...
    def setupCPAL(
        self,
        palettes,
        paletteTypes: Incomplete | None = ...,
        paletteLabels: Incomplete | None = ...,
        paletteEntryLabels: Incomplete | None = ...,
    ) -> None: ...
    def setupStat(
        self, axes, locations: Incomplete | None = ..., elidedFallbackName: int = ...
    ) -> None: ...
