# tile-renderer
Tile renderer for leaflet.js usage, made by 7d

**Documentation: https://tile-renderer.readthedocs.io/en/latest/**

## Current version: v1.0
* **v1.0 ()**
  * added stripes for areas
  * added offset for image centertext
  * new function: `renderer.tools.line_findEnds()`
  * new function: `renderer.mathtools.pointsAway()`
    * replaces the messy and unresponsive find-two-points-n-units-away-from-a-point-on-a-straight-line calculations of sympy using trigo
    * rendering should be faster now (`renderer.render.midpoint()`'s speed is now 0-1% of the original speed)
    * **REJECT SYMPY, EMBRACE TRIGONOMETRY, ALL HAIL TRIGO**
  * added a few more level 2 logs to `renderer.render()`
  * new function: `renderer.tileMerge()`, used to merge tiles
  * changed output of `renderer.render()` from list to dict
  * in counting of rendering operations in `renderer.render()`, added 1 to each tilePlas to account for text
  * rewrote `renderer.mathtools.dash()` and `renderer.mathtools.dashOffset()`, they're no longer broken :D
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