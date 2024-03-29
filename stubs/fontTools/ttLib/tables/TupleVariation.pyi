from _typeshed import Incomplete
from fontTools.misc.fixedTools import otRound as otRound
from fontTools.misc.textTools import safeEval as safeEval

EMBEDDED_PEAK_TUPLE: int
INTERMEDIATE_REGION: int
PRIVATE_POINT_NUMBERS: int
DELTAS_ARE_ZERO: int
DELTAS_ARE_WORDS: int
DELTA_RUN_COUNT_MASK: int
POINTS_ARE_WORDS: int
POINT_RUN_COUNT_MASK: int
TUPLES_SHARE_POINT_NUMBERS: int
TUPLE_COUNT_MASK: int
TUPLE_INDEX_MASK: int
log: Incomplete

class TupleVariation:
    axes: Incomplete
    coordinates: Incomplete
    def __init__(self, axes, coordinates) -> None: ...
    def __eq__(self, other): ...
    def getUsedPoints(self): ...
    def hasImpact(self): ...
    def toXML(self, writer, axisTags) -> None: ...
    def fromXML(self, name, attrs, _content) -> None: ...
    def compile(
        self, axisTags, sharedCoordIndices=..., pointData: Incomplete | None = ...
    ): ...
    def compileCoord(self, axisTags): ...
    def compileIntermediateCoord(self, axisTags): ...
    @staticmethod
    def decompileCoord_(axisTags, data, offset): ...
    @staticmethod
    def compilePoints(points): ...
    @staticmethod
    def decompilePoints_(numPoints, data, offset, tableTag): ...
    def compileDeltas(self): ...
    @staticmethod
    def compileDeltaValues_(deltas, bytearr: Incomplete | None = ...): ...
    @staticmethod
    def encodeDeltaRunAsZeroes_(deltas, offset, bytearr): ...
    @staticmethod
    def encodeDeltaRunAsBytes_(deltas, offset, bytearr): ...
    @staticmethod
    def encodeDeltaRunAsWords_(deltas, offset, bytearr): ...
    @staticmethod
    def decompileDeltas_(numDeltas, data, offset): ...
    @staticmethod
    def getTupleSize_(flags, axisCount): ...
    def getCoordWidth(self): ...
    def scaleDeltas(self, scalar) -> None: ...
    def roundDeltas(self) -> None: ...
    def calcInferredDeltas(self, origCoords, endPts) -> None: ...
    def optimize(
        self, origCoords, endPts, tolerance: float = ..., isComposite: bool = ...
    ) -> None: ...
    def __imul__(self, scalar): ...
    def __iadd__(self, other): ...

def decompileSharedTuples(axisTags, sharedTupleCount, data, offset): ...
def compileSharedTuples(axisTags, variations, MAX_NUM_SHARED_COORDS=...): ...
def compileTupleVariationStore(
    variations, pointCount, axisTags, sharedTupleIndices, useSharedPoints: bool = ...
): ...
def decompileTupleVariationStore(
    tableTag,
    axisTags,
    tupleVariationCount,
    pointCount,
    sharedTuples,
    data,
    pos,
    dataPos,
): ...
def decompileTupleVariation_(
    pointCount, sharedTuples, sharedPoints, tableTag, axisTags, data, tupleData
): ...
def inferRegion_(peak): ...
