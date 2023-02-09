from _typeshed import Incomplete
from fontTools.pens.basePen import BasePen

class PerimeterPen(BasePen):
    value: int
    tolerance: Incomplete
    def __init__(
        self, glyphset: Incomplete | None = ..., tolerance: float = ...
    ) -> None: ...
