from __future__ import annotations

import math
from collections import Counter
from typing import Tuple

import numpy as np
from nptyping import Int, NDArray, Shape
from pydantic import BaseModel, validator

from renderer import RealNum, tools as tools
from renderer.types.coord import TileCoord, WorldLine, Bounds, WorldCoord
from renderer.types.zoom_params import ZoomParams


class Component(BaseModel):
    namespace: str
    id: str
    display_name: str
    description: str
    type: str
    layer: float
    nodes: WorldLine
    attrs: dict
    tags: list[str]

    @property
    def nodes_as_ndarray(self) -> NDArray[Shape["*, 2"], Int]:
        return np.array(self.nodes)
    
    @property
    def fid(self) -> str:
        return f"{self.namespace}-{self.id}"

    def find_components_attached(self, other_components: Pla2File) -> list[tuple[Component, WorldCoord]]:
        return [(other_component, coord)
                for other_component in other_components.components
                for coord in self.nodes
                if coord in other_component.nodes]

    @staticmethod
    def find_ends(
            components: list[Component]
    ) -> Bounds[int]:
        """
        Finds the minimum and maximum X and Y values of a JSON of components

        :param ComponentList components: a JSON of components
        :param NodeList nodes: a JSON of nodes

        :returns: Returns in the form `(x_max, x_min, y_max, y_min)`
        :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
        """
        bounds = [component.nodes.bounds for component in components]
        return Bounds(
            x_max=max(b.x_max for b in bounds),
            x_min=min(b.x_min for b in bounds),
            y_max=max(b.y_max for b in bounds),
            y_min=min(b.y_min for b in bounds)
        )

    @staticmethod
    def rendered_in(
            components: list[Component],
            zoom_params: ZoomParams
    ) -> list[TileCoord]:
        """
        Like :py:func:`tools.line.to_tiles`, but for a JSON of components.

        :param ComponentList components: a JSON of components
        :param NodeList nodes: a JSON of nodes
        :param int min_zoom: minimum zoom value
        :param int max_zoom: maximum zoom value
        :param RealNum max_zoom_range: actual distance covered by a tile in the maximum zoom

        :returns: A list of tile coordinates
        :rtype: List[TileCoord]

        :raises ValueError: if max_zoom < min_zoom
        """

        return list(set(*component.nodes.to_tiles(zoom_params) for component in components))


class Pla2File(BaseModel):
    components: list[Component]

    @validator("components")
    def unique_ns_id(cls, components: list[Component]) -> list[Component]:
        count = {
            k: v
            for k, v in Counter(component.fid for component in components).items()
            if v >= 2
        }
        if count:
            raise ValueError(
                f"IDs {', '.join(f'`{id_}`' for id_ in count)} is duplicated"
            )
        return components

    def __getitem__(self, id_: str) -> Component:
        return [comp for comp in self.components if comp.fid == id_][0]
    
    def __delitem__(self, id_: str):
        self.components.remove(self[id_])

    @property
    def ids(self) -> list[str]:
        return [comp.fid for comp in self.components]
