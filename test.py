import renderer
import json

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

def skinFileRead():
    with open("skins/default.json", "r") as f:
        data = json.load(f)
        f.close()
        return data

#renderer.utils.tileCoordListIntegrity([(0,1,1), (2,3,4)], 1, 5, error=True)

#print(renderer.tools.lineToTiles([(3,4), (10,5)], 0, 2, 8))

renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 2, 2, 8)