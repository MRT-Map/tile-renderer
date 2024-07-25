import json
import os
from pathlib import Path
from typing import Literal

import click
import msgspec.json

import tile_renderer.pla1to2
import tile_renderer.render_svg
import tile_renderer.render_tiles
import tile_renderer.skin.generate_default
from tile_renderer.__about__ import __version__
from tile_renderer.coord import Coord
from tile_renderer.pla2 import Pla2File, _SerComponent
from tile_renderer.skin import Skin, _SerSkin


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="tile-renderer")
def cli():
    pass


@cli.command(help="renders an SVG map from PLA2_FILES")
@click.argument(
    "pla2-files",
    nargs=-1,
    type=Path,
)
@click.option("-s", "--skin", type=Path, default=None, help="")
@click.option("-z", "--zoom", type=int, default=0, show_default=True, help="")
@click.option("-o", "--out-file", type=Path, default=None, show_default=True, help="")
def svg(*, pla2_files: tuple[Path, ...], skin: Path | None, zoom: int, out_file: Path | None):
    components = []
    for path in pla2_files:
        components.extend(Pla2File.from_file(path).components)
    out = tile_renderer.render_svg.render_svg(
        components=components, skin=Skin.default() if skin is None else Skin.from_file(skin), zoom=zoom
    )
    if out_file is None:
        click.echo(str(out))
    else:
        out_file.write_text(str(out))


@cli.command(help="renders PNG tiles from PLA2_FILES")
@click.argument(
    "pla2-files",
    nargs=-1,
    type=Path,
)
@click.option("-s", "--skin", type=Path, default=None, help="")
@click.option("-z", "--zoom", type=int, default=0, show_default=True, help="")
@click.option("-r", "--max-zoom-range", type=int, required=True, help="")
@click.option("-t", "--tile-size", type=int, required=True, help="")
@click.option("-f", "--offset", type=float, nargs=2, default=(0, 0), show_default=True, help="")
@click.option("-p", "--processes", type=int, default=(os.cpu_count() or 8) * 2, show_default=True, help="")
@click.option("-c", "--chunk-size", type=int, default=8, show_default=True, help="")
@click.option("-o", "--out-dir", type=Path, default=Path.cwd(), show_default=True, help="")
def tiles(
    *,
    pla2_files: tuple[Path, ...],
    skin: Path | None,
    zoom: int,
    max_zoom_range: int,
    tile_size: int,
    offset: tuple[float, float],
    processes: int,
    chunk_size: int,
    out_dir: Path,
):
    components = []
    for path in pla2_files:
        components.extend(Pla2File.from_file(path).components)
    for tile, b in tile_renderer.render_tiles.render_tiles(
        components=components,
        skin=Skin.default() if skin is None else Skin.from_file(skin),
        zoom=zoom,
        max_zoom_range=max_zoom_range,
        tile_size=tile_size,
        offset=Coord(offset[0], offset[1]),
        processes=processes,
        chunk_size=chunk_size,
    ).items():
        (out_dir / f"{tile}.png").write_bytes(b)


@cli.command(help="convert pla1-formatted COMPS and NODES file to pla2 format")
@click.argument(
    "comps",
    type=Path,
)
@click.argument(
    "nodes",
    type=Path,
)
@click.option("-o", "--out-dir", type=Path, default=Path.cwd(), show_default=True, help="")
@click.option("-j", "--json", "json_format", is_flag=True, default=False, show_default=True, help="")
def pla1to2(*, comps: Path, nodes: Path, out_dir: Path, json_format: bool):
    comps_dict = json.loads(comps.read_bytes())
    nodes_dict = json.loads(nodes.read_bytes())
    for result in tile_renderer.pla1to2.pla1to2(comps_dict, nodes_dict):
        if json_format:
            result.save_json(out_dir)
        else:
            result.save_json(out_dir)


@cli.command(help="generate the default skin")
def generate_default_skin():
    tile_renderer.skin.generate_default.main()


@cli.command(help="print JSON schemas for a skin or PLA2 file")
@click.argument("what", type=click.Choice(["skin", "pla2"], case_sensitive=False))
@click.option("-o", "--out-file", type=Path, default=None, show_default=True, help="")
def schema(*, what: Literal["skin", "pla2"], out_file: Path | None):
    s = msgspec.json.schema(list[_SerComponent] if what == "pla2" else _SerSkin)

    def remove_ser(o):
        if isinstance(o, dict):
            return {remove_ser(k): remove_ser(v) for k, v in o.items()}
        if isinstance(o, list):
            return [remove_ser(i) for i in o]
        if isinstance(o, str):
            return o.replace("_Ser", "")
        return o

    s = remove_ser(s)
    if out_file is None:
        click.echo(msgspec.json.encode(s).decode())
    else:
        out_file.write_bytes(msgspec.json.encode(s))
