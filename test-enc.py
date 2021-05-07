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
import os
renderer.tileMerge(os.getcwd()+"\\tiles\\", saveDir="tiles/")

#if __name__ == "__main__": print(renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 0, 8, 32, saveDir="tiles/", saveImages=False, processes=10))