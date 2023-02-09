from _typeshed import Incomplete
from fontTools.pens.basePen import BasePen

class QuartzPen(BasePen):
    path: Incomplete
    xform: Incomplete
    def __init__(
        self, glyphSet, path: Incomplete | None = ..., xform: Incomplete | None = ...
    ) -> None: ...
