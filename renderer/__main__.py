import argparse
import glob
import json
from pathlib import Path

import psutil
import vector
from rich.progress import track
from rich.traceback import install

from renderer import Config, TileCoord, __version__, merge_tiles, render

# noinspection PyProtectedMember
from renderer._internal.logger import log
from renderer.misc_types.pla2 import Pla2File
from renderer.misc_types.skin import Skin
from renderer.misc_types.zoom_params import ZoomParams
from renderer.pla1to2 import pla1to2

install(show_locals=True)


def p_render(p: argparse.ArgumentParser):
    p.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="the PLA 2 file to render from",
    )
    p.add_argument(
        "-m", "--min_zoom", type=int, required=True, help="Minimum zoom value"
    )
    p.add_argument(
        "-M", "--max_zoom", type=int, required=True, help="Maximum zoom value"
    )
    p.add_argument(
        "-r",
        "--max_zoom_range",
        type=float,
        required=True,
        help="Actual distance covered by a tile in the maximum zoom",
    )
    p.add_argument(
        "-e",
        "--export_id",
        type=str,
        help="The name of the rendering task",
        default="unnamed",
    )
    p.add_argument(
        "-td",
        "--temp_dir",
        type=Path,
        help="the temporary data folder that will be used to save data",
        default=Path.cwd() / "temp",
    )
    p.add_argument(
        "-s",
        "--skin",
        type=str,
        help="The skin to use for rendering the tiles",
        default="default",
    )
    p.add_argument(
        "-ad",
        "--assets_dir",
        type=Path,
        help="The asset directory for the skin",
        default=Path(__file__).parent.parent / "skins" / "assets",
    )
    p.add_argument(
        "-sd",
        "--save_dir",
        type=Path,
        help="The directory to save tiles to",
        default=Path.cwd() / "tiles",
    )
    p.add_argument(
        "-p",
        "--processes",
        type=int,
        help="The number of processes to run for rendering",
        default=psutil.cpu_count(),
    )

    def tile_coord(x: str):
        return TileCoord(
            int(x.split(",")[0]), int(x.split(",")[1]), int(x.split(",")[2])
        )

    p.add_argument(
        "-t",
        "--tiles",
        nargs="+",
        type=tile_coord,
        help="a list of tiles to render, given as `z,x,y [z,x,y...]`",
        default=[],
    )
    p.add_argument(
        "-z",
        "--zooms",
        nargs="+",
        type=int,
        help="a list of zooms to render, given as `z [z...]`",
        default=[],
    )
    p.add_argument(
        "-o",
        "--offset",
        nargs=2,
        type=int,
        help="the offset of node coordinates, given as `x y`",
        default=[0, 0],
    )
    p.add_argument(
        "-p1b",
        "--part1_batch_size",
        type=int,
        help="The batch size for part 1",
        default=8,
    )
    p.add_argument(
        "-p1c",
        "--part1_chunk_size",
        type=int,
        help="The chunk size for part 1",
        default=8,
    )
    p.add_argument(
        "-p1s",
        "--part1_serial",
        help="Whether part 1 will be run serially",
        action="store_true",
    )
    p.add_argument(
        "-p3b",
        "--part3_batch_size",
        type=int,
        help="The batch size for part 3",
        default=8,
    )
    p.add_argument(
        "-p3s",
        "--part3_serial",
        help="Whether part 3 will be run serially",
        action="store_true",
    )


def p_merge(p: argparse.ArgumentParser):
    p.add_argument(
        "-i",
        "--image_dir",
        type=Path,
        help="the directory of tiles",
        default=Path.cwd(),
    )
    p.add_argument(
        "-s",
        "--save_dir",
        type=Path,
        help="the directory to save the merged image to",
        default=Path.cwd(),
    )
    p.add_argument(
        "-z", "--zoom", type=int, nargs="*", help="the zoom levels to merge", default=[]
    )


def p_1to2(p: argparse.ArgumentParser):
    p.add_argument(
        "-c",
        "--comps",
        type=Path,
        help="the directory of PLA 1 components",
    )
    p.add_argument(
        "-n",
        "--nodes",
        type=Path,
        help="the directory of PLA 1 nodes",
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        help="the directory to output PLA 2 files",
        default=Path.cwd(),
    )
    p.add_argument(
        "--json",
        help="save PLA 2 as json instead of msgpack",
        default=False,
        action="store_true",
    )


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help="task to run", dest="task")

    subparsers.add_parser(
        "info",
        help="view info about the renderer",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    p_render(
        subparsers.add_parser(
            "render",
            help="render tiles",
            formatter_class=argparse.MetavarTypeHelpFormatter,
        )
    )

    p_merge(
        subparsers.add_parser(
            "merge",
            help="merge tiles",
            formatter_class=argparse.MetavarTypeHelpFormatter,
        )
    )

    p_1to2(
        subparsers.add_parser(
            "1to2",
            help="convert PLA 1 to PLA 2",
            formatter_class=argparse.MetavarTypeHelpFormatter,
        )
    )

    args = parser.parse_args()

    if args.task == "info":
        log.info(f"[yellow]tile-renderer [cyan]v{__version__}")
        log.info(
            "[yellow]Made by 7d for the OpenMRTMap project of the Minecart Rapid Transit Mapping Services"
        )
        log.info("GitHub: https://github.com/MRT-Map/tile-renderer")
        log.info("PyPI: https://pypi.org/project/tile-renderer/")
        log.info("Docs: https://tile-renderer.readthedocs.io/en/latest/")
        log.info("More about OpenMRTMap: https://github.com/MRT-Map")
    elif args.task == "render":
        log.info("Getting components...")
        file = Pla2File.from_file(args.file)
        log.info("Getting skin...")
        skin = Skin.from_name(args.skin)
        log.info("Starting rendering...")
        render(
            file,
            Config(
                ZoomParams(args.min_zoom, args.max_zoom, args.max_zoom_range),
                args.export_id,
                args.temp_dir,
                skin,
                args.assets_dir,
            ),
            save_dir=args.save_dir,
            processes=args.processes,
            tiles=args.tiles,
            zooms=args.zooms,
            offset=vector.obj(x=args.offset[0], y=args.offset[1]),
            part1_batch_size=args.part1_batch_size,
            part1_chunk_size=args.part1_chunk_size,
            part1_serial=args.part1_serial,
            part3_batch_size=args.part3_batch_size,
            part3_serial=args.part3_serial,
        )
    elif args.task == "merge":
        merge_tiles(args.image_dir, True, args.save_dir, args.zoom)
    elif args.task == "1to2":
        comps = {}
        for file in track(
            glob.glob(str(args.comps / "*.comps.pla")), "Loading components"
        ):
            with open(file, "r") as f:
                comps.update(json.load(f))
        nodes = {}
        for file in track(glob.glob(str(args.nodes / "*.nodes.pla")), "Loading nodes"):
            with open(file, "r") as f:
                nodes.update(json.load(f))
        result = pla1to2(comps, nodes)
        args.out.mkdir(exist_ok=True)
        for file in result:
            if args.json:
                file.save_json(args.out)
            else:
                file.save_msgpack(args.out)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
