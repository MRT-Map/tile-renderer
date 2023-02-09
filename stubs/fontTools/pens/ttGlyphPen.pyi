from typing import Any, Dict, Optional, Tuple

from _typeshed import Incomplete
from fontTools.misc.loggingTools import LogMixin
from fontTools.pens.basePen import LoggingPen
from fontTools.pens.pointPen import AbstractPointPen
from fontTools.ttLib.tables._g_l_y_f import Glyph

class _TTGlyphBasePen:
    glyphSet: Incomplete
    handleOverflowingTransforms: Incomplete
    def __init__(
        self,
        glyphSet: Optional[Dict[str, Any]],
        handleOverflowingTransforms: bool = ...,
    ) -> None: ...
    points: Incomplete
    endPts: Incomplete
    types: Incomplete
    components: Incomplete
    def init(self) -> None: ...
    def addComponent(
        self,
        baseGlyphName: str,
        transformation: Tuple[float, float, float, float, float, float],
        identifier: Optional[str] = ...,
        **kwargs: Any
    ) -> None: ...
    def glyph(self, componentFlags: int = ...) -> Glyph: ...

class TTGlyphPen(_TTGlyphBasePen, LoggingPen):
    drawMethod: str
    transformPen: Incomplete
    def lineTo(self, pt: Tuple[float, float]) -> None: ...
    def moveTo(self, pt: Tuple[float, float]) -> None: ...
    def curveTo(self, *points) -> None: ...
    def qCurveTo(self, *points) -> None: ...
    def closePath(self) -> None: ...
    def endPath(self) -> None: ...

class TTGlyphPointPen(_TTGlyphBasePen, LogMixin, AbstractPointPen):
    drawMethod: str
    transformPen: Incomplete
    def init(self) -> None: ...
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
