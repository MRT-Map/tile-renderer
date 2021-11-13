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

p = exampleplaRead()
n = examplenodesRead()
s = renderer.misc.get_skin("default")

#if __name__ == "__main__": a = renderer.render(p, n, s, 8, 8, 16, save_dir="tiles/")

print(renderer.tools.geo_json.to_component_node_json(renderer.tools.component_json.to_geo_json(p, n, s)))
