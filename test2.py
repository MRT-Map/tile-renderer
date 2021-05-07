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
s = renderer.misc.getSkin("default")

#if __name__ == "__main__": a = renderer.render(p, n, s, 8, 8, 16, saveDir="tiles/")

print(renderer.tools.geoJson.toNodePlaJson(renderer.tools.plaJson.toGeoJson(p, n, s)))
