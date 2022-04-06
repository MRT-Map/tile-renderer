import argparse
import glob
from pathlib import Path

import blessed

import psutil


def cmd():
    import renderer
    term = blessed.Terminal()

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='task to run', dest="task")

    subparsers.add_parser('info', help='view info about the renderer', formatter_class=argparse.MetavarTypeHelpFormatter)

    subparsers.add_parser('nodebuilder', help='launch the node builder', formatter_class=argparse.MetavarTypeHelpFormatter)
    subparsers.add_parser('compbuilder', help='launch the component builder', formatter_class=argparse.MetavarTypeHelpFormatter)

    p_validate = subparsers.add_parser('validate', help='validate a JSON file', formatter_class=argparse.MetavarTypeHelpFormatter)
    p_validate.add_argument('-c', '--components', type=Path, help='component JSON file to validate')
    p_validate.add_argument('-n', '--nodes', required=True, type=Path, help='node JSON file to validate')

    p_vdir = subparsers.add_parser('vdir', help='validate a directory of JSON files', formatter_class=argparse.MetavarTypeHelpFormatter)
    p_vdir.add_argument('-c', '--components', type=Path, help='directory of folder of component JSON files to validate')
    p_vdir.add_argument('-n', '--nodes', required=True, type=Path, help='directory of folder of node JSON files to validate')
    p_vdir.add_argument('-cs', '--components_suffix', type=str, help='The suffix for component files\' names', default='.comps.pla')
    p_vdir.add_argument('-ns', '--nodes_suffix', type=str, help='The suffix for node files\' names', default='.nodes.pla')

    p_render = subparsers.add_parser('render', help='render tiles', formatter_class=argparse.MetavarTypeHelpFormatter)
    p_render.add_argument('-c', '--components', required=True, type=Path, help='the component JSON file directory')
    p_render.add_argument('-n', '--nodes', required=True, type=Path, help='the node JSON file directory')
    p_render.add_argument('-min', '--min_zoom', type=int, required=True, help="minimum zoom value")
    p_render.add_argument('-max', '--max_zoom', type=int, required=True, help="maximum zoom value")
    p_render.add_argument('-r', '--max_zoom_range', type=float, required=True, help="range of coordinates covered by a tile in the maximum zoom")
    p_render.add_argument('-s', '--skin', type=str, help='the name of the skin to use', default='default')
    p_render.add_argument('-d', '--save_dir', type=Path, help="the directory to save tiles in", default=Path.cwd())
    p_render.add_argument('-m', '--processes', type=int, help="the amount of processes to run for rendering", default=psutil.cpu_count())
    p_render.add_argument('-t', '--tiles', type=list, help="a list of tiles to render, given in tuples of (z,x,y)")
    p_render.add_argument('-o', '--offset', type=tuple, help="the offset of node coordinates, given as (x,y)", default=[0, 0])
    p_render.add_argument('-dbg', '--debug', help="Prints extra debug information on tiles", default=False, action="store_true")

    p_merge = subparsers.add_parser('merge', help='merge tiles', formatter_class=argparse.MetavarTypeHelpFormatter)
    p_merge.add_argument('-i', '--image_dir', type=Path, help='the directory of tiles', default=Path.cwd())
    p_merge.add_argument('-s', '--save_dir', type=Path, help='the directory to save the merged image to', default=Path.cwd())
    p_merge.add_argument('-z', '--zoom', type=int, nargs='*', help='the zoom levels to merge', default=[])

    args = parser.parse_args()

    if args.task == "info":
        print(term.yellow(f"tile-renderer v{renderer.__version__}"))
        print(term.yellow("Made by 7d for the OpenMRTMap project"))
        print("Github: https://github.com/MRT-Map/tile-renderer")
        print("PyPI: https://pypi.org/project/tile-renderer/")
        print("Docs: https://tile-renderer.readthedocs.io/en/latest/")
        print("More about OpenMRTMap: https://github.com/MRT-Map")
    elif args.task == "nodebuilder":
        import renderer.builders.node # type: ignore
    elif args.task == "compbuilder":
        import renderer.builders.comp # type: ignore
    elif args.task == "render" and __name__ == '__main__':
        print("Getting nodes...")
        node_json = renderer.internals.internal._read_json(args.nodes)
        nodes = renderer.NodeList(renderer.internals.internal._read_json(args.nodes))
        print("Getting components...")
        comps = renderer.ComponentList(renderer.internals.internal._read_json(args.components), node_json)
        print("Getting skin...")
        skin = renderer.Skin.from_name(args.skin)
        print("Starting rendering...")
        renderer.render(comps, nodes,
                        args.min_zoom, args.max_zoom, args.max_zoom_range,
                        skin=skin,
                        save_dir=args.save_dir,
                        processes=args.processes,
                        tiles=args.tiles,
                        offset=args.offset,
                        debug=args.debug)
    elif args.task == "validate":
        n = renderer.internals.internal._read_json(args.nodes)
        if args.components is not None:
            p = renderer.internals.internal._read_json(args.components)
            renderer.ComponentList.validate_json(p, n)
        else:
            renderer.NodeList.validate_json(n)
        print(term.green("Validated"))
    elif args.task == "vdir":
        if args.components is not None:
            if not args.components.endswith("/"): args.components += "/"
            components = {}
            for d in glob.glob(glob.escape(args.components)):
                if d.endswith(args.components_suffix):
                    components.update(renderer.internals.internal._read_json(d))

        if not args.nodes.endswith("/"): args.nodes += "/"
        nodes = {}
        for d in glob.glob(glob.escape(args.nodes)+"*.json"):
            if d.endswith(args.nodes_suffix+".json"):
                nodes.update(renderer.internals.internal._read_json(d))

        if args.components is not None:
            renderer.ComponentList.validate_json(components, nodes)
        else:
            renderer.NodeList.validate_json(nodes)
        print(term.green("Validated"))
    elif args.task == "merge":
        renderer.merge_tiles(args.image_dir, save_dir=args.save_dir, zoom=args.zoom)
    else:
        parser.print_help()

cmd()