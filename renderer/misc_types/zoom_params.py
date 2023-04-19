from dataclasses import dataclass


@dataclass(frozen=True)
class ZoomParams:
    # noinspection PyUnresolvedReferences
    """
    Utility object for storing zoom parameters.

    :param int min: Minimum zoom value
    :param int max: Maximum zoom value
    :param float range: Actual distance covered by a tile in the maximum zoom

    :raises ValueError: If min > max
    """
    min: int
    max: int
    range: float

    def __post_init__(self) -> None:
        if self.min > self.max:
            raise ValueError("Max zoom value is greater than min zoom value")
