import argparse
from typing import Union
import renderer
import blessed
term = blessed.Terminal()

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='task to run', dest="task")

p_info = subparsers.add_parser('info', help='view info about the renderer', formatter_class=argparse.MetavarTypeHelpFormatter)

p_nodebuider = subparsers.add_parser('nodebuilder', help='launch the node builder', formatter_class=argparse.MetavarTypeHelpFormatter)

p_setlang = subparsers.add_parser('setlang', help='Set the language of the renderer', formatter_class=argparse)
p_setlang.add_argument('lang', required=True, type=str, help="The language to set to")

p_render = subparsers.add_parser('render', help='render tiles', formatter_class=argparse.MetavarTypeHelpFormatter.MetavarTypeHelpFormatter)
p_render.add_argument('-p', '--plaJson', required=True, type=str, help='the PLA Json file directory')
p_render.add_argument('-n', '--nodeJson', required=True, type=str, help='the node Json file directory')
p_render.add_argument('-s', '--skinJson', type=str, help='the name of the skin to use', default='default')
p_render.add_argument('-min', '--minZoom', type=int, required=True, help="minimum zoom value")
p_render.add_argument('-max', '--maxZoom', type=int, required=True, help="maximum zoom value")
p_render.add_argument('-r', '--maxZoomRange', type=float, required=True, help="ange of coordinates covered by a tile in the maximum zoom")
p_render.add_argument('-d', '--saveDir', type=str, help="the directory to save tiles in", default='')
p_render.add_argument('-m', '--processes', type=int, help="the amount of processes to run for rendering", default=1)
p_render.add_argument('-t', '--tiles', type=list, help="a list of tiles to render, given in tuples of (z,x,y)")

args = parser.parse_args()
import os
print(os.getcwd())
if args.task == "info":
    print(term.yellow(f"tile-renderer v{renderer.__version__}"))
    print(term.yellow("Made by 7d for the OpenMRTMap project"))
    print("Github: https://github.com/MRT-Map/tile-renderer")
    print("PyPI: https://pypi.org/project/tile-renderer/")
    print("Docs: https://tile-renderer.readthedocs.io/en/latest/")
if args.task == "nodebuilder":
    import renderer.internals.nodeJsonBuilder
elif args.task == "render" and __name__ == '__main__':
    renderer.render(renderer.internals.internal.readJson(args.plaJson), renderer.internals.internal.readJson(args.nodeJson), renderer.misc.getSkin(args.skinJson), args.minZoom, args.maxZoom, args.maxZoomRange, saveDir=args.saveDir, processes=args.processes, tiles=args.tiles)