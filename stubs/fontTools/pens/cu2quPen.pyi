from _typeshed import Incomplete
from fontTools.cu2qu import curve_to_quadratic as curve_to_quadratic
from fontTools.pens.basePen import AbstractPen as AbstractPen
from fontTools.pens.basePen import (
    decomposeSuperBezierSegment as decomposeSuperBezierSegment,
)
from fontTools.pens.pointPen import BasePointToSegmentPen as BasePointToSegmentPen
from fontTools.pens.pointPen import ReverseContourPointPen as ReverseContourPointPen
from fontTools.pens.reverseContourPen import ReverseContourPen as ReverseContourPen

class Cu2QuPen(AbstractPen):
    pen: Incomplete
    max_err: Incomplete
    stats: Incomplete
    ignore_single_points: Incomplete
    start_pt: Incomplete
    current_pt: Incomplete
    def __init__(
        self,
        other_pen,
        max_err,
        reverse_direction: bool = ...,
        stats: Incomplete | None = ...,
        ignore_single_points: bool = ...,
    ) -> None: ...
    def moveTo(self, pt) -> None: ...
    def lineTo(self, pt) -> None: ...
    def qCurveTo(self, *points) -> None: ...
    def curveTo(self, *points) -> None: ...
    def closePath(self) -> None: ...
    def endPath(self) -> None: ...
    def addComponent(self, glyphName, transformation) -> None: ...

class Cu2QuPointPen(BasePointToSegmentPen):
    pen: Incomplete
    max_err: Incomplete
    stats: Incomplete
    def __init__(
        self,
        other_point_pen,
        max_err,
        reverse_direction: bool = ...,
        stats: Incomplete | None = ...,
    ) -> None: ...
    def addComponent(self, baseGlyphName, transformation) -> None: ...
