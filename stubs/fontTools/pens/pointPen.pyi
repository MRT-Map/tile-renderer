from typing import Any, Optional, Tuple

from _typeshed import Incomplete
from fontTools.pens.basePen import AbstractPen

class AbstractPointPen:
    def beginPath(self, identifier: Optional[str] = ..., **kwargs: Any) -> None: ...
    def endPath(self) -> None: ...
    def addPoint(
        self,
        pt: Tuple[float, float],
        segmentType: Optional[str] = ...,
        smooth: bool = ...,
        name: Optional[str] = ...,
        identifier: Optional[str] = ...,
        **kwargs: Any
    ) -> None: ...
    def addComponent(
        self,
        baseGlyphName: str,
        transformation: Tuple[float, float, float, float, float, float],
        identifier: Optional[str] = ...,
        **kwargs: Any
    ) -> None: ...

class BasePointToSegmentPen(AbstractPointPen):
    currentPath: Incomplete
    def __init__(self) -> None: ...
    def beginPath(self, identifier: Incomplete | None = ..., **kwargs) -> None: ...
    def endPath(self) -> None: ...
    def addPoint(
        self,
        pt,
        segmentType: Incomplete | None = ...,
        smooth: bool = ...,
        name: Incomplete | None = ...,
        identifier: Incomplete | None = ...,
        **kwargs
    ) -> None: ...

class PointToSegmentPen(BasePointToSegmentPen):
    pen: Incomplete
    outputImpliedClosingLine: Incomplete
    def __init__(self, segmentPen, outputImpliedClosingLine: bool = ...) -> None: ...
    def addComponent(
        self, glyphName, transform, identifier: Incomplete | None = ..., **kwargs
    ) -> None: ...

class SegmentToPointPen(AbstractPen):
    pen: Incomplete
    contour: Incomplete
    def __init__(self, pointPen, guessSmooth: bool = ...) -> None: ...
    def moveTo(self, pt) -> None: ...
    def lineTo(self, pt) -> None: ...
    def curveTo(self, *pts) -> None: ...
    def qCurveTo(self, *pts) -> None: ...
    def closePath(self) -> None: ...
    def endPath(self) -> None: ...
    def addComponent(self, glyphName, transform) -> None: ...

class GuessSmoothPointPen(AbstractPointPen):
    def __init__(self, outPen, error: float = ...) -> None: ...
    def beginPath(self, identifier: Incomplete | None = ..., **kwargs) -> None: ...
    def endPath(self) -> None: ...
    def addPoint(
        self,
        pt,
        segmentType: Incomplete | None = ...,
        smooth: bool = ...,
        name: Incomplete | None = ...,
        identifier: Incomplete | None = ...,
        **kwargs
    ) -> None: ...
    def addComponent(
        self, glyphName, transformation, identifier: Incomplete | None = ..., **kwargs
    ) -> None: ...

class ReverseContourPointPen(AbstractPointPen):
    pen: Incomplete
    currentContour: Incomplete
    def __init__(self, outputPointPen) -> None: ...
    currentContourIdentifier: Incomplete
    onCurve: Incomplete
    def beginPath(self, identifier: Incomplete | None = ..., **kwargs) -> None: ...
    def endPath(self) -> None: ...
    def addPoint(
        self,
        pt,
        segmentType: Incomplete | None = ...,
        smooth: bool = ...,
        name: Incomplete | None = ...,
        identifier: Incomplete | None = ...,
        **kwargs
    ) -> None: ...
    def addComponent(
        self, glyphName, transform, identifier: Incomplete | None = ..., **kwargs
    ) -> None: ...
