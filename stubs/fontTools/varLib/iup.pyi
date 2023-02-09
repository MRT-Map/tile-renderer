from numbers import Integral, Real

from fontTools.misc import cython as cython

COMPILED: bool
MAX_LOOKBACK: int

def iup_segment(
    coords: _PointSegment, rc1: _Point, rd1: _Delta, rc2: _Point, rd2: _Delta
) -> _DeltaSegment: ...
def iup_contour(
    deltas: _DeltaOrNoneSegment, coords: _PointSegment
) -> _DeltaSegment: ...
def iup_delta(
    deltas: _DeltaOrNoneSegment, coords: _PointSegment, ends: _Endpoints
) -> _DeltaSegment: ...
def can_iup_in_between(
    deltas: _DeltaSegment,
    coords: _PointSegment,
    i: Integral,
    j: Integral,
    tolerance: Real,
) -> bool: ...
def iup_contour_optimize(
    deltas: _DeltaSegment, coords: _PointSegment, tolerance: Real = ...
) -> _DeltaOrNoneSegment: ...
def iup_delta_optimize(
    deltas: _DeltaSegment,
    coords: _PointSegment,
    ends: _Endpoints,
    tolerance: Real = ...,
) -> _DeltaOrNoneSegment: ...
