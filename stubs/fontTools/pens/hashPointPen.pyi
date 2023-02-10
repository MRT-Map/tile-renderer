from _typeshed import Incomplete
from fontTools.pens.basePen import MissingComponentError as MissingComponentError
from fontTools.pens.pointPen import AbstractPointPen as AbstractPointPen

class HashPointPen(AbstractPointPen):
    glyphset: Incomplete
    data: Incomplete
    def __init__(
        self, glyphWidth: int = ..., glyphSet: Incomplete | None = ...
    ) -> None: ...
    @property
    def hash(self): ...
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
        self,
        baseGlyphName,
        transformation,
        identifier: Incomplete | None = ...,
        **kwargs
    ) -> None: ...
