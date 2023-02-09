from _typeshed import Incomplete
from fontTools.pens.basePen import AbstractPen as AbstractPen
from fontTools.pens.basePen import BasePen as BasePen
from fontTools.pens.momentsPen import OpenContourError as OpenContourError
from fontTools.pens.pointPen import SegmentToPointPen as SegmentToPointPen
from fontTools.pens.recordingPen import RecordingPen as RecordingPen
from fontTools.pens.statisticsPen import StatisticsPen as StatisticsPen

class PerContourPen(BasePen):
    value: Incomplete
    def __init__(self, Pen, glyphset: Incomplete | None = ...) -> None: ...

class PerContourOrComponentPen(PerContourPen):
    def addComponent(self, glyphName, transformation) -> None: ...

class RecordingPointPen(BasePen):
    value: Incomplete
    def __init__(self) -> None: ...
    def beginPath(self, identifier: Incomplete | None = ..., **kwargs) -> None: ...
    def endPath(self) -> None: ...
    def addPoint(self, pt, segmentType: Incomplete | None = ...) -> None: ...

def min_cost_perfect_bipartite_matching(G): ...
def test(
    glyphsets, glyphs: Incomplete | None = ..., names: Incomplete | None = ...
): ...
def main(args: Incomplete | None = ...): ...