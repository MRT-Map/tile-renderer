from __future__ import annotations

import math
from collections import Counter
from typing import TYPE_CHECKING, Self, dataclass_transform

import msgspec
from msgspec import Struct

from tile_renderer._logger import log
from tile_renderer.coord import Line, TileCoord

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@dataclass_transform()
class Component(Struct):
    namespace: str
    id: str
    display_name: str
    description: str
    type: str
    layer: float
    nodes: Line[int]
    tags: list[str]
    attrs: dict | None = None

    @property
    def fid(self) -> str:
        return f"{self.namespace}-{self.id}"

    def encode(self) -> _SerComponent:
        return _SerComponent(
            namespace=self.namespace,
            id=self.id,
            display_name=self.display_name,
            description=self.description,
            type=self.type,
            layer=self.layer,
            nodes=self.nodes.encode(),  # type: ignore
            tags=self.tags,
            attrs=self.attrs,
        )

    def tiles(self, zoom: int, max_zoom_range: int) -> set[TileCoord]:
        if len(self.nodes) == 0:
            return set()
        bounds = self.nodes.bounds
        zoom_range = max_zoom_range * 2**zoom
        xr = range(math.floor(bounds.x_min), math.ceil(bounds.x_max + 1), zoom_range // 2)
        yr = range(math.floor(bounds.y_min), math.ceil(bounds.y_max + 1), zoom_range // 2)
        return {TileCoord(zoom, math.floor(x / zoom_range), math.floor(y / zoom_range)) for x in xr for y in yr}


@dataclass_transform()
class _SerComponent(Component):
    nodes: list[tuple[int | float, int | float]]  # type: ignore[assignment]

    def decode(self) -> Component:
        return Component(
            namespace=self.namespace,
            id=self.id,
            display_name=self.display_name,
            description=self.description,
            type=self.type,
            layer=self.layer,
            nodes=Line.decode(self.nodes),  # type: ignore[arg-type]
            tags=self.tags,
            attrs=self.attrs,
        )


_json_decoder = msgspec.json.Decoder(list[_SerComponent])
_msgpack_decoder = msgspec.msgpack.Decoder(list[_SerComponent])
_json_encoder = msgspec.json.Encoder()
_msgpack_encoder = msgspec.msgpack.Encoder()


@dataclass_transform()
class Pla2File(Struct):
    namespace: str
    components: list[Component]

    @classmethod
    def from_file(cls, file: Path) -> Self:
        if file.suffix == ".msgpack":
            return cls.from_msgpack(file)
        return cls.from_json(file)

    @classmethod
    def from_json(cls, file: Path) -> Self:
        with file.open("rb") as f:
            b = f.read()
        return cls(
            namespace=file.stem.split(".")[0],
            components=[c.decode() for c in _json_decoder.decode(b)],
        )

    @classmethod
    def from_msgpack(cls, file: Path) -> Self:
        with file.open("rb") as f:
            b = f.read()
        return cls(
            namespace=file.stem.split(".")[0],
            components=[c.decode() for c in _msgpack_decoder.decode(b)],
        )

    def save_json(self, directory: Path) -> None:
        with (directory / f"{self.namespace}.pla2.json").open("wb+") as f:
            f.write(_json_encoder.encode([c.encode() for c in self.components]))

    def save_msgpack(self, directory: Path) -> None:
        with (directory / f"{self.namespace}.pla2.msgpack").open("wb+") as f:
            f.write(_msgpack_encoder.encode([c.encode() for c in self.components]))

    def __post_init__(self):
        count = {k: v for k, v in Counter(component.fid for component in self.components).items() if v >= 2}  # noqa: PLR2004
        if count:
            log.warning(f"IDs {', '.join(f'`{id_}`' for id_ in count)} are duplicated")

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
        return [comp.fid for comp in self.components]
