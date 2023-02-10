from _typeshed import Incomplete
from fontTools.misc.transform import Identity as Identity
from fontTools.misc.transform import Scale as Scale

TWO_PI: Incomplete
PI_OVER_TWO: Incomplete

class EllipticalArc:
    current_point: Incomplete
    rx: Incomplete
    ry: Incomplete
    rotation: Incomplete
    large: Incomplete
    sweep: Incomplete
    target_point: Incomplete
    angle: Incomplete
    center_point: Incomplete
    def __init__(
        self, current_point, rx, ry, rotation, large, sweep, target_point
    ) -> None: ...
    def draw(self, pen) -> None: ...
