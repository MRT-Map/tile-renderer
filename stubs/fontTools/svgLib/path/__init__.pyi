from _typeshed import Incomplete
from fontTools.misc import etree as etree
from fontTools.misc.textTools import tostr as tostr
from fontTools.pens.transformPen import TransformPen as TransformPen

from .parser import parse_path as parse_path
from .shapes import PathBuilder as PathBuilder

class SVGPath:
    root: Incomplete
    transform: Incomplete
    def __init__(
        self, filename: Incomplete | None = ..., transform: Incomplete | None = ...
    ) -> None: ...
    @classmethod
    def fromstring(cls, data, transform: Incomplete | None = ...): ...
    def draw(self, pen) -> None: ...
