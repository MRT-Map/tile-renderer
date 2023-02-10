import json
import multiprocessing
import time
from pathlib import Path

import pytest

import renderer
import renderer.merge_tiles
import renderer.misc_types.pla2
import renderer.render
from renderer.misc_types.skin import Skin


def exampleplaRead() -> dict:
    with open("data/example.comps.pla", "r") as f:
        data = json.load(f)
        f.close()
        return data


def examplenodesRead() -> dict:
    with open("data/example.nodes.pla", "r") as f:
        data = json.load(f)
        f.close()
        return data


def test_pytest():
    if __name__ == "__main__":
        print("Loading nodes")
        rn = examplenodesRead()
        print("Loading components")
        rp = exampleplaRead()
        n = renderer.NodeList(rn)
        p = renderer.ComponentList(rp, rn)
        s = Skin.from_name("default")

        # base
        a = renderer.render.render(
            p, n, renderer.ZoomParams(8, 8, 8), save_dir=Path("tiles/"), processes=8
        )
        renderer.merge_tiles.merge_tiles(a, save_images=False)
        return
        # tools
        renderer.misc_types.pla2.find_ends(p, n)
        t = renderer.misc_types.pla2.rendered_in(p, n, 8, 8, 16)
        g = renderer.tools.component_json.to_geo_json(p, n, s)
        renderer.tools.geo_json.to_component_node_json(g)

        l = [(0, 0), (1, 1), (2, 2), (3, 3)]
        renderer.misc_types.pla2.find_ends(t)
        renderer.misc_types.pla2.find_ends(l)
        renderer.tools.line.to_tiles(l, 8, 8, 16)

        nl = n.keys()
        renderer.tools.nodes.find_components_attached(nl, p)
        renderer.tools.nodes.to_coords(nl, n)

        renderer.tools.coord.to_tiles((342, 552), 8, 8, 16)

        # math_utils
        renderer.math_utils.midpoint(0, 1, 2, 3, 5, n=5)  # incl points_away
        renderer.math_utils.point_in_poly(0, 0, l)  # incl lines_intersect
        renderer.math_utils.poly_center(l)
        renderer.math_utils.line_in_box(l, 1, -1, -1, 1)
        renderer.math_utils.dash_offset(l, 1, 1)  # incl dash
        renderer.math_utils.rotate_around_pivot(5, 5, 10, 10, 9)

        # validate
        renderer.validate.v_coords(l)
        renderer.validate.v_tile_coords(t, 8, 8)
        renderer.validate.v_node_list(nl, n)
        renderer.validate.v_node_json(n)
        renderer.validate.v_component_json(p, n)
        renderer.validate.v_skin_json(s)
        renderer.validate.v_geo_json(g)

        print("complete")


test_pytest()
