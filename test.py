import renderer
import json
import time
import pytest

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
    #with open("renderer/skins/default.json", "r") as f:
    #    data = json.load(f)
    #    f.close()
    #    return data
    return renderer.misc.getSkin("default")

#if __name__ == "__main__": a = renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 8, 8, 16, saveDir="tiles/")

def test_pytest():
	if __name__ == "__main__": a = renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 8, 8, 8, saveDir="tiles/", saveImages=False); print(a)