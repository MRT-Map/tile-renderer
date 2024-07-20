from __future__ import annotations

import math
from collections import Counter
from typing import TYPE_CHECKING, Self, dataclass_transform

import msgspec
from msgspec import Struct

from tile_renderer.types.coord import Line, TileCoord

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@dataclass_transform()
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
    nodes: Line[int]
    """The nodes of the component"""
    tags: list[str]
    """The tags of the component"""
    attrs: dict | None = None
    """Additional attributes of the component, will probably be used in newer versions"""

    @property
    def fid(self) -> str:
        """The full ID of the component (<namespace>-<id>)"""
        return f"{self.namespace}-{self.id}"

    def encode(self) -> _SerComponent:
        return _SerComponent(
            namespace=self.namespace,
            id=self.id,
            display_name=self.display_name,
            description=self.description,
            type=self.type,
            layer=self.layer,
            nodes=self.nodes.encode(),
            tags=self.tags,
            attrs=self.attrs,
        )

    @staticmethod
    def tiles(components: list[Component], zoom: int, max_zoom_range: int) -> set[TileCoord]:
        bounds = sum((c.nodes.bounds for c in components), components[0].nodes.bounds)
        zoom_range = max_zoom_range * 2**zoom
        xr = range(math.floor(bounds.x_min), math.ceil(bounds.x_max + 1), zoom_range // 2)
        yr = range(math.floor(bounds.y_min), math.ceil(bounds.y_max + 1), zoom_range // 2)
        return {TileCoord(zoom, math.floor(x / zoom_range), math.floor(y / zoom_range)) for x in xr for y in yr}


@dataclass_transform()
class _SerComponent(Component):
    nodes: list[tuple[int | float, int | float]]

    def decode(self) -> Component:
        return Component(
            namespace=self.namespace,
            id=self.id,
            display_name=self.display_name,
            description=self.description,
            type=self.type,
            layer=self.layer,
            nodes=Line.decode(self.nodes),
            tags=self.tags,
            attrs=self.attrs,
        )


_json_decoder = msgspec.json.Decoder(list[_SerComponent])
_msgpack_decoder = msgspec.msgpack.Decoder(list[_SerComponent])
_json_encoder = msgspec.json.Encoder()
_msgpack_encoder = msgspec.msgpack.Encoder()


@dataclass_transform()
class Pla2File(Struct):
    """Represents a PLA2 file"""

    namespace: str
    """The namespace of the file, all components included belong to this namespace"""
    components: list[Component]
    """The components in the file"""

    @classmethod
    def from_file(cls, file: Path) -> Self:
        """
        Load a PLA2 file from a path, can be either in JSON or MessagePack format
        """
        if file.suffix == ".msgpack":
            return cls.from_msgpack(file)
        return cls.from_json(file)

    @classmethod
    def from_json(cls, file: Path) -> Self:
        """
        Load a PLA2 file, must be in JSON
        """
        with file.open("rb") as f:
            b = f.read()
        return cls(
            namespace=file.stem.split(".")[0],
            components=[c.decode() for c in _json_decoder.decode(b)],
        )

    @classmethod
    def from_msgpack(cls, file: Path) -> Self:
        """
        Load a PLA2 file, must be in MessagePack
        """
        with file.open("rb") as f:
            b = f.read()
        return cls(
            namespace=file.stem.split(".")[0],
            components=[c.decode() for c in _msgpack_decoder.decode(b)],
        )

    def save_json(self, directory: Path) -> None:
        """
        Save the PLA2 file in JSON format to a directory
        """
        with (directory / f"{self.namespace}.pla2.json").open("wb+") as f:
            f.write(_json_encoder.encode([c.encode() for c in self.components]))

    def save_msgpack(self, directory: Path) -> None:
        """
        Save the PLA2 file in MessagePack format to a directory
        """
        with (directory / f"{self.namespace}.pla2.msgpack").open("wb+") as f:
            f.write(_msgpack_encoder.encode([c.encode() for c in self.components]))

    def __post_init__(self):
        count = {k: v for k, v in Counter(component.fid for component in self.components).items() if v >= 2}  # noqa: PLR2004
        if count:
            msg = f"IDs {', '.join(f'`{id_}`' for id_ in count)} are duplicated"
            raise ValueError(
                msg,
            )

    def __getitem__(self, id_: str) -> Component:
        return next(comp for comp in self.components if comp.fid == id_)

    def __delitem__(self, id_: str) -> None:
        self.components.remove(self[id_])

    def __iter__(self) -> Iterator[Component]:
        yield from self.components

    def __len__(self) -> int:
        return len(self.components)

    @property
    def ids(self) -> list[str]:
        """A list of IDs that all the components have"""
        return [comp.fid for comp in self.components]
