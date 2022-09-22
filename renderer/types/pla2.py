from collections import Counter

import numpy as np
from nptyping import Int, NDArray, Shape
from pydantic import BaseModel, validator


class Component(BaseModel):
    namespace: str
    id: str
    display_name: str
    description: str
    layer: float
    nodes: list[tuple[int, int]]
    attrs: dict
    tags: list[str]

    def nodes_as_ndarray(self) -> NDArray[Shape["*, 2"], Int]:
        return np.array(self.nodes)


class Pla2File(BaseModel):
    components: list[Component]

    @validator("components")
    def unique_ns_id(cls, components: list[Component]) -> list[Component]:
        count = {
            k: v
            for k, v in Counter(component.id for component in components).items()
            if v >= 2
        }
        if count:
            raise ValueError(
                f"IDs {', '.join(f'`{id_}`' for id_ in count)} is duplicated"
            )
        return components
