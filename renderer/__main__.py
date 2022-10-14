import argparse
from pathlib import Path

import psutil
import vector


def main():
    import renderer
    from renderer.internals.logger import log
    from renderer.types.pla2 import Pla2File
    from renderer.types.skin import Skin
    from renderer.types.zoom_params import ZoomParams

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help="task to run", dest="task")

    subparsers.add_parser(
        "info",
        help="view info about the renderer",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    p_validate = subparsers.add_parser(
        "validate",
        help="validate a JSON file",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    p_validate.add_argument(
        "-c", "--components", type=Path, help="component JSON file to validate"
    )
    p_validate.add_argument(
        "-n", "--nodes", required=True, type=Path, help="node JSON file to validate"
    )

    p_vdir = subparsers.add_parser(
        "vdir",
        help="validate a directory of JSON files",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    p_vdir.add_argument(
        "-c",
        "--components",
        type=Path,
        help="directory of folder of component JSON files to validate",
    )
    p_vdir.add_argument(
        "-n",
        "--nodes",
        required=True,
        type=Path,
        help="directory of folder of node JSON files to validate",
    )
    p_vdir.add_argument(
        "-cs",
        "--components_suffix",
        type=str,
        help="The suffix for component files' names",
        default=".comps.pla",
    )
    p_vdir.add_argument(
        "-ns",
        "--nodes_suffix",
        type=str,
        help="The suffix for node files' names",
        default=".nodes.pla",
    )

    p_render = subparsers.add_parser(
        "render", help="render tiles", formatter_class=argparse.MetavarTypeHelpFormatter
    )
    p_render.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="the PLA 2 file to render from",
    )
    p_render.add_argument(
        "-min", "--min_zoom", type=int, required=True, help="minimum zoom value"
    )
    p_render.add_argument(
        "-max", "--max_zoom", type=int, required=True, help="maximum zoom value"
    )
    p_render.add_argument(
        "-r",
        "--max_zoom_range",
        type=float,
        required=True,
        help="range of coordinates covered by a tile in the maximum zoom",
    )
    p_render.add_argument(
        "-s", "--skin", type=str, help="the name of the skin to use", default="default"
    )
    p_render.add_argument(
        "-d",
        "--save_dir",
        type=Path,
        help="the directory to save tiles in",
        default=Path.cwd(),
    )
    p_render.add_argument(
        "-m",
        "--processes",
        type=int,
        help="the amount of processes to run for rendering",
        default=psutil.cpu_count(),
    )
    p_render.add_argument(
        "-t",
        "--tiles",
        type=list,
        help="a list of tiles to render, given in tuples of (z,x,y)",
    )
    p_render.add_argument(
        "-o",
        "--offset",
        type=tuple,
        help="the offset of node coordinates, given as (x,y)",
        default=[0, 0],
    )
    p_render.add_argument(
        "-dbg",
        "--debug",
        help="log.infos extra debug information on tiles",
        default=False,
        action="store_true",
    )

    p_merge = subparsers.add_parser(
        "merge", help="merge tiles", formatter_class=argparse.MetavarTypeHelpFormatter
    )
    p_merge.add_argument(
        "-i",
        "--image_dir",
        type=Path,
        help="the directory of tiles",
        default=Path.cwd(),
    )
    p_merge.add_argument(
        "-s",
        "--save_dir",
        type=Path,
        help="the directory to save the merged image to",
        default=Path.cwd(),
    )
    p_merge.add_argument(
        "-z", "--zoom", type=int, nargs="*", help="the zoom levels to merge", default=[]
    )

    args = parser.parse_args()

    if args.task == "info":
        log.info(f"[yellow]tile-renderer v{renderer.__version__}")
        log.info(
            "[yellow]Made by 7d for the OpenMRTMap project of the Minecart Rapid Transit Mapping Services"
        )
        log.info("Github: https://github.com/MRT-Map/tile-renderer")
        log.info("PyPI: https://pypi.org/project/tile-renderer/")
        log.info("Docs: https://tile-renderer.readthedocs.io/en/latest/")
        log.info("More about OpenMRTMap: https://github.com/MRT-Map")
    elif args.task == "render":
        log.info("Getting components...")
        file = Pla2File(renderer.internals.internal._read_json(args.components))
        log.info("Getting skin...")
        skin = Skin.from_name(args.skin)
        log.info("Starting rendering...")
        renderer.render(
            file,
            ZoomParams(args.min_zoom, args.max_zoom, args.max_zoom_range),
            skin=skin,
            save_dir=args.save_dir,
            processes=args.processes,
            tiles=args.tiles,
            offset=vector.obj(x=args.offset[0], y=args.offset[1]),
        )
    elif args.task == "validate":
        pass  # TODO
    elif args.task == "vdir":
        pass  # TODO
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
