import renderer
import json

def exampleplaRead():
    with open("examplepla.json", "r") as f:
        data = json.load(f)
        f.close()
        return data

def examplenodesRead():
    with open("examplenodes.json", "r") as f:
        data = json.load(f)
        f.close()
        return data

print(renderer.tools.lineToTiles([(3,4), (10,5)], 0, 2, 8))

#renderer.render(exampleplaRead(), examplenodesRead(), 0, 2, 8)