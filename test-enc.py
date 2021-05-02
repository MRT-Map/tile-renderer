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
    with open("renderer/skins/default.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        f.close()
        return data

#renderer.utils.tileCoordListIntegrity([(0,1,1), (2,3,4)], 1, 5, error=True)
#print(renderer.tools.lineToTiles([(3,4), (10,5)], 0, 2, 8))
#print(renderer.mathtools.pointInPoly(1,4,[(0,0),(2,0),(1,5)]))
#print(renderer.tools.findPlasAttachedToNode("a", exampleplaRead()))
import os
import re
#a = renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 0, 3, 128, saveDir="tiles/", verbosityLevel=2)
renderer.tileMerge(os.getcwd()+"\\tiles\\", saveDir="tiles/")

#if __name__ == "__main__": print(renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 0, 8, 32, saveDir="tiles/", saveImages=False, processes=10))