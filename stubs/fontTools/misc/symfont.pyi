from _typeshed import Incomplete
from fontTools.pens.basePen import BasePen as BasePen

n: int
t: Incomplete
x: Incomplete
y: Incomplete
c: Incomplete
X: Incomplete
Y: Incomplete
P: Incomplete
C: Incomplete
BinomialCoefficient: Incomplete
last: Incomplete
this: Incomplete
BernsteinPolynomial: Incomplete
BezierCurve: Incomplete
BezierCurveC: Incomplete

def green(f, curveXY): ...

class _BezierFuncsLazy(dict):
    def __init__(self, symfunc) -> None: ...
    def __missing__(self, i): ...

class GreenPen(BasePen):
    value: int
    def __init__(self, func, glyphset: Incomplete | None = ...) -> None: ...

AreaPen: Incomplete
MomentXPen: Incomplete
MomentYPen: Incomplete
MomentXXPen: Incomplete
MomentYYPen: Incomplete
MomentXYPen: Incomplete

def printGreenPen(
    penName, funcs, file=..., docstring: Incomplete | None = ...
) -> None: ...
