from __future__ import annotations

import itertools
from collections import Counter
from typing import TYPE_CHECKING, Any

import msgspec.json
from msgspec import Struct
from shapely import LineString

from .coord import Bounds, Coord, TileCoord, WorldCoord, WorldLine

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from .zoom_params import ZoomParams


class Component(Struct):
    """A component to be rendered"""

    namespace: str
    """The namespace that the coordinate belongs to"""
    id: str
    """The ID of the component"""
    display_name: str
    """This will appear on the map itself, if the component type's style has a Text layer"""
    description: str
    """The description of the component"""
    type: str
    """The component type of the map"""
    layer: float
    """The layer of the component. Higher numbers mean further in front"""
    nodes: WorldLine
    """The nodes of the component"""
    tags: list[str]
    """The tags of the component"""
    attrs: dict | None = None
    """Additional attributes of the component, will probably be used in newer versions"""

    @property
    def fid(self) -> str:
        """The full ID of the component (<namespace>-<id>)"""
        return f"{self.namespace}-{self.id}"

    @staticmethod
    def find_ends(components: list[Component]) -> Bounds[float]:
        """
        Finds the minimum and maximum X and Y values from a set of components
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
        components: list[Component],
        zoom_params: ZoomParams,
    ) -> list[TileCoord]:
        """
        Finds the tile coordinates that the list of components will be rendered in.
        """
        tiles = [component.nodes.to_tiles(zoom_params) for component in components]
        return list(set(itertools.chain(*tiles)))


def _enc_hook(obj: Any) -> Any:
    if isinstance(obj, WorldLine):
        return [_enc_hook(c) for c in obj.coords]
    if isinstance(obj, Coord):
        return Coord.enc_hook(obj)
    raise TypeError(type(obj))


def _dec_hook(type_: type, obj: Any) -> Any:
    if type_ == WorldCoord:
        c = Coord.dec_hook(obj)
        return WorldCoord(c.x, c.y)
    if type_ in (WorldLine, LineString):
        if len(obj) == 1:
            obj.append(obj[0])
        return WorldLine([_dec_hook(WorldCoord, o) for o in obj])
    raise TypeError(type(obj))


_json_decoder = msgspec.json.Decoder(list[Component], dec_hook=_dec_hook)
_msgpack_decoder = msgspec.msgpack.Decoder(list[Component], dec_hook=_dec_hook)
_json_encoder = msgspec.json.Encoder(enc_hook=_enc_hook)
_msgpack_encoder = msgspec.msgpack.Encoder(enc_hook=_enc_hook)


class Pla2File(Struct):
    """Represents a PLA2 file"""

    namespace: str
    """The namespace of the file, all components included belong to this namespace"""
    components: list[Component]
    """The components in the file"""

    @staticmethod
    def from_file(file: Path) -> Pla2File:
        """
        Load a PLA2 file from a path, can be either in JSON or MessagePack format
        """
        if file.suffix == ".msgpack":
            return Pla2File.from_msgpack(file)
        return Pla2File.from_json(file)

    @staticmethod
    def from_json(file: Path) -> Pla2File:
        """
        Load a PLA2 file, must be in JSON
        """
        with file.open("rb") as f:
            b = f.read()
        return Pla2File(
            namespace=file.stem.split(".")[0],
            components=list(Pla2File.validate(_json_decoder.decode(b))),
        )

    @staticmethod
    def from_msgpack(file: Path) -> Pla2File:
        """
        Load a PLA2 file, must be in MessagePack
        """
        with file.open("rb") as f:
            b = f.read()
        return Pla2File(
            namespace=file.stem.split(".")[0],
            components=list(Pla2File.validate(_msgpack_decoder.decode(b))),
        )

    def save_json(self, directory: Path) -> None:
        """
        Save the PLA2 file in JSON format to a directory
        """
        with (directory / f"{self.namespace}.pla2.json").open("wb+") as f:
            f.write(_json_encoder.encode(self.components))

    def save_msgpack(self, directory: Path) -> None:
        """
        Save the PLA2 file in MessagePack format to a directory
        """
        with (directory / f"{self.namespace}.pla2.msgpack").open("wb+") as f:
            f.write(_msgpack_encoder.encode(self.components))

    @staticmethod
    def validate(comps: list[Component]) -> list[Component]:
        """
        Check for duplicate IDs in a list of components and returns the same list of components if all is well

        :raises ValueError: If a duplicated ID is found
        """
        count = {
            k: v
            for k, v in Counter(component.fid for component in comps).items()
            if v >= 2
        }
        if count:
            raise ValueError(
                f"IDs {', '.join(f'`{id_}`' for id_ in count)} are duplicated",
            )
        return comps

    def __getitem__(self, id_: str) -> Component:
        return [comp for comp in self.components if comp.fid == id_][0]

    def __delitem__(self, id_: str) -> None:
        self.components.remove(self[id_])

    def __iter__(self) -> Generator[Component, Any, None]:
        yield from self.components

    def __len__(self) -> int:
        return len(self.components)

    @property
    def ids(self) -> list[str]:
        """A list of IDs that all the components have"""
        return [comp.fid for comp in self.components]
