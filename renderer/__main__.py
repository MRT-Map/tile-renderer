import argparse
import glob
import renderer
import blessed
import os
term = blessed.Terminal()

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='task to run', dest="task")

p_info = subparsers.add_parser('info', help='view info about the renderer', formatter_class=argparse.MetavarTypeHelpFormatter)

p_nodebuider = subparsers.add_parser('nodebuilder', help='launch the node builder', formatter_class=argparse.MetavarTypeHelpFormatter)

p_validate = subparsers.add_parser('validate', help='validate a JSON file', formatter_class=argparse.MetavarTypeHelpFormatter)
p_validate.add_argument('-p', '--pla', type=str, help='PLA JSON file to validate')
p_validate.add_argument('-n', '--nodes', required=True, type=str, help='node JSON file to validate')

p_vdir = subparsers.add_parser('vdir', help='validate a directory of JSON files', formatter_class=argparse.MetavarTypeHelpFormatter)
p_vdir.add_argument('-p', '--pla', type=str, help='directory of folder of PLA JSON files to validate')
p_vdir.add_argument('-n', '--nodes', required=True, type=str, help='directory of folder of node JSON files to validate')
p_vdir.add_argument('-ps', '--plaSuffix', type=str, help='The suffix for PLA files\' names', default='pla')
p_vdir.add_argument('-ns', '--nodesSuffix', type=str, help='The suffix for node files\' names', default='nodes')

p_render = subparsers.add_parser('render', help='render tiles', formatter_class=argparse.MetavarTypeHelpFormatter)
p_render.add_argument('-p', '--plaJson', required=True, type=str, help='the PLA Json file directory')
p_render.add_argument('-n', '--nodeJson', required=True, type=str, help='the node Json file directory')
p_render.add_argument('-s', '--skinJson', type=str, help='the name of the skin to use', default='default')
p_render.add_argument('-min', '--minZoom', type=int, required=True, help="minimum zoom value")
p_render.add_argument('-max', '--maxZoom', type=int, required=True, help="maximum zoom value")
p_render.add_argument('-r', '--maxZoomRange', type=float, required=True, help="ange of coordinates covered by a tile in the maximum zoom")
p_render.add_argument('-d', '--saveDir', type=str, help="the directory to save tiles in", default='')
p_render.add_argument('-m', '--processes', type=int, help="the amount of processes to run for rendering", default=1)
p_render.add_argument('-t', '--tiles', type=list, help="a list of tiles to render, given in tuples of (z,x,y)")

p_merge = subparsers.add_parser('merge', help='merge tiles', formatter_class=argparse.MetavarTypeHelpFormatter)
p_merge.add_argument('-i', '--imageDir', type=str, help='the directory of tiles', default=os.getcwd())
p_merge.add_argument('-s', '--saveDir', type=str, help='the directory to save the merged image to', default='')
p_merge.add_argument('-z', '--zoom', type=int, nargs='*', help='the zoom levels to merge', default=[])

args = parser.parse_args()

if args.task == "info":
    print(term.yellow(f"tile-renderer v{renderer.__version__}"))
    print(term.yellow("Made by 7d for the OpenMRTMap project"))
    print("Github: https://github.com/MRT-Map/tile-renderer")
    print("PyPI: https://pypi.org/project/tile-renderer/")
    print("Docs: https://tile-renderer.readthedocs.io/en/latest/")
elif args.task == "nodebuilder":
    import renderer.internals.nodeJsonBuilder # type: ignore
elif args.task == "render" and __name__ == '__main__':
    renderer.render(renderer.internals.internal.readJson(args.plaJson),
                    renderer.internals.internal.readJson(args.nodeJson),
                    renderer.misc.getSkin(args.skinJson), args.minZoom,
                    args.maxZoom, args.maxZoomRange,
                    saveDir=args.saveDir,
                    processes=args.processes,
                    tiles=args.tiles)
elif args.task == "validate":
    n = renderer.internals.internal.readJson(args.nodes)
    if args.pla is not None:
        p = renderer.internals.internal.readJson(args.pla)
        renderer.validate.vPlaJson(p, n)
    else:
        renderer.validate.vNodeJson(n)
    print(term.green("Validated"))
elif args.task == "vdir":
    if args.pla is not None:
        if not args.pla.endswith("/"): args.pla += "/"
        plas = {}
        for d in glob.glob(glob.escape(args.pla)+"*.json"):
            if d.endswith(args.plaSuffix+".json"):
                plas.update(renderer.internals.internal.readJson(d))

    if not args.nodes.endswith("/"): args.nodes += "/"
    nodes = {}
    for d in glob.glob(glob.escape(args.nodes)+"*.json"):
        if d.endswith(args.nodesSuffix+".json"):
            nodes.update(renderer.internals.internal.readJson(d))

    if args.pla is not None:
        renderer.validate.vPlaJson(plas, nodes)
    else:
        renderer.validate.vNodeJson(nodes)
    print(term.green("Validated"))
elif args.task == "merge":
    renderer.tileMerge(args.imageDir, saveDir=args.saveDir, zoom=args.zoom)
else:
    parser.print_help()