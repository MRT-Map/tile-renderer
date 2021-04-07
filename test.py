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

#renderer.utils.tileCoordListIntegrity([(0,1,1), (2,3,4)], 1, 5)
#print(renderer.tools.lineToTiles([(3,4), (10,5)], 0, 2, 8))
#print(renderer.mathtools.pointInPoly(1,4,[(0,0),(2,0),(1,5)]))
#print(renderer.tools.findPlasAttachedToNode("a", exampleplaRead()))
renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 1, 2, 8, tiles=[(2,0,0),(1,0,0)], saveDir="tiles/")
#print(renderer.mathtools.dash(5, 3, 3, 5, 1))