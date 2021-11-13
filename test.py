import renderer
import json
import time
import pytest

def exampleplaRead():
    with open("data/examplepla.json", "r") as f:
        data = json.load(f)
        f.close()
        return data

def examplenodesRead():
    with open("data/examplenodes.json", "r") as f:
        data = json.load(f)
        f.close()
        return data

def test_pytest():
    if __name__ == "__main__":
        p = exampleplaRead()
        n = examplenodesRead()
        s = renderer.misc.getSkin("default")

        #base
        a = renderer.render(p, n, s, 8, 8, 8, save_dir="tiles/", processes=10)
        renderer.tile_merge(a, save_images=False)
        
        #tools
        renderer.tools.component_json.find_ends(p, n)
        t = renderer.tools.component_json.rendered_in(p, n, 8, 8, 16)
        g = renderer.tools.component_json.to_geo_json(p, n, s)
        renderer.tools.geo_json.to_component_node_json(g)

        l = [(0,0), (1,1), (2,2), (3,3)]
        renderer.tools.tile.find_ends(t)
        renderer.tools.line.find_ends(l)
        renderer.tools.line.to_tiles(l, 8, 8, 16)

        nl = n.keys()
        renderer.tools.nodes.find_components_attached(nl, p)
        renderer.tools.nodes.to_coords(nl, n)

        renderer.tools.coord.to_tiles((342, 552), 8, 8, 16)
        
        #mathtools
        renderer.mathtools.midpoint(0, 1, 2, 3, 5, n=5) #incl pointsAway
        renderer.mathtools.point_in_poly(0, 0, l) #incl lines_intersect
        renderer.mathtools.poly_center(l)
        renderer.mathtools.line_in_box(l, 1, -1, -1, 1)
        renderer.mathtools.dash_offset(l, 1, 1) #incl dash
        renderer.mathtools.rotate_around_pivot(5, 5, 10, 10, 9)

        #validate
        renderer.validate.v_coords(l)
        renderer.validate.v_tile_coords(t, 8, 8)
        renderer.validate.v_node_list(nl, n)
        renderer.validate.v_node_json(n)
        renderer.validate.v_component_json(p, n)
        renderer.validate.v_skin_json(s)
        renderer.validate.v_geo_json(g)

        #misc
        renderer.misc.getSkin('default')

        print("complete")
        
test_pytest()