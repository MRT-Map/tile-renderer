from __future__ import annotations

import itertools
from collections import Counter
from pathlib import Path
from typing import Any, Generator, Tuple, Type

import msgspec.json
import numpy as np
from msgspec import Struct
from nptyping import Int, NDArray, Shape

from renderer.types.coord import Bounds, Coord, TileCoord, WorldCoord, WorldLine
from renderer.types.zoom_params import ZoomParams


class Component(Struct):
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

    def find_components_attached(
        self, other_components: Pla2File
    ) -> list[tuple[Component, WorldCoord]]:
        return [
            (other_component, coord)
            for other_component in other_components.components
            for coord in self.nodes
            if coord in other_component.nodes
        ]

    @staticmethod
    def find_ends(components: list[Component]) -> Bounds[int]:
        """
        Finds the minimum and maximum X and Y values of a JSON of components

        :param ComponentList components: a JSON of components

        :returns: TODO
        :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
        """
        bounds = [component.nodes.bounds for component in components]
        return Bounds(
            x_max=max(b.x_max for b in bounds),
            x_min=min(b.x_min for b in bounds),
            y_max=max(b.y_max for b in bounds),
            y_min=min(b.y_min for b in bounds),
        )

    @staticmethod
    def rendered_in(
        components: list[Component], zoom_params: ZoomParams
    ) -> list[TileCoord]:
        """
        Like :py:func:`tools.line.to_tiles`, but for a JSON of components.

        :param ComponentList components: a JSON of components
        :param zoom_params: TODO

        :returns: A list of tile coordinates
        :rtype: List[TileCoord]

        :raises ValueError: if max_zoom < min_zoom
        """
        tiles = [component.nodes.to_tiles(zoom_params) for component in components]
        return list(set(itertools.chain(*tiles)))


def _enc_hook(obj: Any) -> Any:
    if isinstance(obj, Coord):
        return Coord.enc_hook(obj)
    return TypeError


def _dec_hook(type_: Type, obj: Any) -> Any:
    if type_ == WorldCoord:
        return Coord.dec_hook(obj)
    elif type_ == WorldLine:
        if len(obj) == 1:
            obj.append(obj[0])
        return WorldLine([_dec_hook(WorldCoord, o) for o in obj])
    return TypeError


_json_decoder = msgspec.json.Decoder(list[Component], dec_hook=_dec_hook)
_msgpack_decoder = msgspec.msgpack.Decoder(list[Component], dec_hook=_dec_hook)
_json_encoder = msgspec.json.Encoder(enc_hook=_enc_hook)
_msgpack_encoder = msgspec.msgpack.Encoder(enc_hook=_enc_hook)


class Pla2File(Struct):
    namespace: str
    components: list[Component]

    @staticmethod
    def from_file(file: Path) -> Pla2File:
        if file.suffix == ".msgpack":
            return Pla2File.from_msgpack(file)
        else:
            return Pla2File.from_json(file)

    @staticmethod
    def from_json(file: Path) -> Pla2File:
        with open(file, "rb") as f:
            b = f.read()
        return Pla2File(
            namespace=file.stem.split(".")[0],
            components=[c for c in Pla2File.validate(_json_decoder.decode(b))],
        )

    @staticmethod
    def from_msgpack(file: Path) -> Pla2File:
        with open(file, "rb") as f:
            b = f.read()
        return Pla2File(
            namespace=file.stem.split(".")[0],
            components=[c for c in Pla2File.validate(_msgpack_decoder.decode(b))],
        )

    def save_json(self, directory: Path):
        with open(directory / f"{self.namespace}.pla2.json", "wb+") as f:
            f.write(_json_encoder.encode(self.components))

    def save_msgpack(self, directory: Path):
        with open(directory / f"{self.namespace}.pla2.msgpack", "wb+") as f:
            f.write(_msgpack_encoder.encode(self.components))

    @staticmethod
    def validate(comps: list[Component]) -> list[Component]:
        count = {
            k: v
            for k, v in Counter(component.fid for component in comps).items()
            if v >= 2
        }
        if count:
            raise ValueError(
                f"IDs {', '.join(f'`{id_}`' for id_ in count)} is duplicated"
            )
        return comps

    def __getitem__(self, id_: str) -> Component:
        return [comp for comp in self.components if comp.fid == id_][0]

    def __delitem__(self, id_: str):
        self.components.remove(self[id_])

    def __iter__(self) -> Generator[Component, Any, None]:
        for component in self.components:
            yield component

    @property
    def ids(self) -> list[str]:
        return [comp.fid for comp in self.components]
