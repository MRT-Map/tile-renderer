import renderer
import json

def exampleplaRead():
    with open("data/encinitaspla.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        f.close()
        return data

def examplenodesRead():
    with open("data/encinitasnodes.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        f.close()
        return data

def skinFileRead():
    with open("skins/default.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        f.close()
        return data

#renderer.utils.tileCoordListIntegrity([(0,1,1), (2,3,4)], 1, 5, error=True)
#print(renderer.tools.lineToTiles([(3,4), (10,5)], 0, 2, 8))
#print(renderer.mathtools.pointInPoly(1,4,[(0,0),(2,0),(1,5)]))
#print(renderer.tools.findPlasAttachedToNode("a", exampleplaRead()))
renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 0, 3, 128, saveDir="tiles/")
