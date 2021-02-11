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

renderer.render(exampleplaRead(), examplenodesRead(), 0, 2, 8)