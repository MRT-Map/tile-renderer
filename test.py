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

def test_pytest():
    if __name__ == "__main__":
        #base
        a = renderer.render(p, n, s, 8, 8, 16, saveDir="tiles/", processes=10)
        renderer.tileMerge(a, saveImages=False)
        
        #tools
        renderer.tools.plaJson.findEnds(p, n)
        t = renderer.tools.plaJson.renderedIn(p, n, 8, 8, 16)
        g = renderer.tools.plaJson.toGeoJson(p, n, s)
        renderer.tools.geoJson.toNodePlaJson(g)

        l = [(0,0), (1,1), (2,2), (3,3)]
        renderer.tools.tile.findEnds(t)
        renderer.tools.line.findEnds(l)
        renderer.tools.line.toTiles(l, 8, 8, 16)

        nl = n.keys()
        renderer.tools.nodes.findPlasAttached(nl, p)
        renderer.tools.nodes.toCoords(nl, n)

        renderer.tools.coord.toTiles((342, 552), 8, 8, 16)
        
        #mathtools
        renderer.mathtools.midpoint(0, 1, 2, 3, 5, n=5) #incl pointsAway
        renderer.mathtools.pointInPoly(0, 0, l) #incl linesIntersect
        renderer.mathtools.polyCenter(l)
        renderer.mathtools.lineInBox(l, 1, -1, -1, 1)
        renderer.mathtools.dashOffset(l, 1, 1) #incl dash
        renderer.mathtools.rotateAroundPivot(5, 5, 10, 10, 9)

        #validate
        renderer.validate.vCoords(l)
        renderer.validate.vTileCoords(t, 8, 8)
        renderer.validate.vNodeList(nl, n)
        renderer.validate.vNodeJson(n)
        renderer.validate.vPlaJson(p, n)
        renderer.validate.vSkinJson(s)
        renderer.validate.vGeoJson(g)

        #misc
        renderer.misc.getSkin('default')
        
