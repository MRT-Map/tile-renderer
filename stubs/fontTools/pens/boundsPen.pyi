from _typeshed import Incomplete
from fontTools.pens.basePen import BasePen

class ControlBoundsPen(BasePen):
    ignoreSinglePoints: Incomplete
    def __init__(self, glyphSet, ignoreSinglePoints: bool = ...) -> None: ...
    bounds: Incomplete
    def init(self) -> None: ...

class BoundsPen(ControlBoundsPen): ...
