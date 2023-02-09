from typing import NamedTuple

from _typeshed import Incomplete
from fontTools.pens.basePen import BasePen

class Contour(NamedTuple):
    points: Incomplete
    tags: Incomplete

class FreeTypePen(BasePen):
    contours: Incomplete
    def __init__(self, glyphSet) -> None: ...
    def outline(self, transform: Incomplete | None = ..., evenOdd: bool = ...): ...
    def buffer(
        self,
        width: Incomplete | None = ...,
        height: Incomplete | None = ...,
        transform: Incomplete | None = ...,
        contain: bool = ...,
        evenOdd: bool = ...,
    ): ...
    def array(
        self,
        width: Incomplete | None = ...,
        height: Incomplete | None = ...,
        transform: Incomplete | None = ...,
        contain: bool = ...,
        evenOdd: bool = ...,
    ): ...
    def show(
        self,
        width: Incomplete | None = ...,
        height: Incomplete | None = ...,
        transform: Incomplete | None = ...,
        contain: bool = ...,
        evenOdd: bool = ...,
    ) -> None: ...
    def image(
        self,
        width: Incomplete | None = ...,
        height: Incomplete | None = ...,
        transform: Incomplete | None = ...,
        contain: bool = ...,
        evenOdd: bool = ...,
    ): ...
    @property
    def bbox(self): ...
    @property
    def cbox(self): ...
