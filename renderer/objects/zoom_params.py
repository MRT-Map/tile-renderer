from dataclasses import dataclass

from renderer.types import RealNum


@dataclass(frozen=True)
class ZoomParams:
    # noinspection PyUnresolvedReferences
    """
    Utility object for storing zoom parameters.

    :param int min: minimum zoom value
    :param int max: maximum zoom value
    :param RealNum range: actual distance covered by a tile in the maximum zoom

    :raises ValueError: if min > max
    """
    min: int
    max: int
    range: RealNum

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError("Max zoom value is greater than min zoom value")