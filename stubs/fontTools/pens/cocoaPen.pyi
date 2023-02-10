from _typeshed import Incomplete
from fontTools.pens.basePen import BasePen

class CocoaPen(BasePen):
    path: Incomplete
    def __init__(self, glyphSet, path: Incomplete | None = ...) -> None: ...
