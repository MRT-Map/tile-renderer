from dataclasses import dataclass


@dataclass(frozen=True)
class ZoomParams:
    """
    Utility object for storing zoom parameters.

    :raises ValueError: If min > max
    """

    min: int
    """Minimum zoom value"""
    max: int
    """Maximum zoom value"""
    range: float
    """Actual distance covered by a tile in the maximum zoom"""

    def __post_init__(self) -> None:
        if self.min > self.max:
            raise ValueError("Max zoom value is greater than min zoom value")
