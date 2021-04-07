# tile-renderer
Tile renderer for leaflet.js usage, made by 7d

**Documentation: https://tile-renderer.readthedocs.io/en/latest/**

## Current version: v0.8
* **v0.8 (7/4/21)**
  * Text of points are now rendered together with texts of lines and areas
  * reordered rendering of PLAs (excluding road tag & text) into functions from if statements
  * got rid of most `**kwargs`
  * redid integrity checking, mostly with Schema
  * new function: `renderer.utils.skinJsonIntegrity()`
  * background of tile can now be customised by skin file
  * added offset to area centertext
  * added centerimage to areas
* **Past changelogs can be found in https://tile-renderer.readthedocs.io/en/latest/changelog.html**

## Usage (simple)
1. Download or clone this repo
2. The important files and folders are `renderer.py` and `skins`. Copypaste those into the same directory as your project file.
3. Write a node JSON file and a PLA JSON file. (Tutorial coming soon) Or, use the example files provided in `data`.
4. In another Python file in the same directory as `renderer.py`, run the renderer. Here is an example code:
```python
import renderer # important!!
import json

def readFile(dir): # extract from JSON as dict
    with open(dir, "r") as f:
        data = json.load(f)
        f.close()
        return data

pla = readFile("path_to_your_PLA_file/pla.json")
nodes = readFile("path_to_your_nodes_file/nodes.json")
skin = readFile("path_to_your_skin_file/skin.json")

renderer.render(pla, nodes, skin, 1, 2, 8)
# renders tiles at zoom levels 1 and 2 with the max zoom tile covering 8 units
# Don't like clogging the main directory? Create a new folder and use this instead:
# renderer.render(pla, nodes, skin, 1, 2, 8, saveDir="your_folder_name/")
```