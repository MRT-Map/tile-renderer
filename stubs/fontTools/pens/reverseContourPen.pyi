from collections.abc import Generator

from _typeshed import Incomplete
from fontTools.pens.filterPen import ContourFilterPen

class ReverseContourPen(ContourFilterPen):
    def filterContour(self, contour): ...

def reversedContour(contour) -> Generator[Incomplete, None, None]: ...
