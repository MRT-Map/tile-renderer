import renderer
import json
import time

def exampleplaRead():
    with open("data/examplepla2.json", "r") as f:
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
#start = time.time()
#a = renderer.render_multiprocess(5, exampleplaRead(), examplenodesRead(), skinFileRead(), 8, 8, 8, saveDir="tiles/")
#print(time.time() - start)
#renderer.tileMerge(a, saveDir="tiles/")
#print(renderer.mathtools.dash(0,0,11,0, 5, 5))
#print(a := renderer.mathtools.dashOffset(coords := [(0,0),(11,0),(11,11),(0,11)], 5, 5))
#for c in range(len(coords)-1):
#    print(renderer.mathtools.dash(coords[c][0], coords[c][1], coords[c+1][0], coords[c+1][1], 5, 5, o=a[c][0], emptyStart=a[c][1]))