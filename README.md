# tile-renderer
Tile renderer for leaflet.js usage, made by 7d

**Note: renderer is complete, but not the skin or the tutorials.**
**Hence mapping is not open to the public yet.**

**Documentation: https://tile-renderer.readthedocs.io/en/latest/**

## Current version: v1.1
* **v1.1 ()**
  * Added log prefixes to `renderer.render()` and `renderer.tileMerge()`
  * Improved curved line drawing
  * `renderer.py` is now split into a package
    * `renderer.utils` renamed to `renderer.validate`
    * all functions of `renderer.tools` and `renderer.validate` renamed
    * method descriptions added to all functions except those in `renderer.internal`
  * New function: `renderer.misc.getSkin()`
  * New logging system that does not clog your terminal
  * changed colour library from `colorama` to `blessed`
  * fixed `renderer.mergeTiles()`, especially in determining which zooms to merge and retrieving images
  * fixed `renderer.misc.getSkin()`
* **Past changelogs can be found in https://tile-renderer.readthedocs.io/en/latest/changelog.html**

## Usage (simple)
1. Download or clone this repo<!--; or run `pip install tile-renderer`-->
2. Write a node JSON file and a PLA JSON file. (Tutorial coming soon) Or, use the example files provided in `data`.
3. In your file, run the renderer. Here is an example code:
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
skin = renderer.misc.getSkin("default")

renderer.render(pla, nodes, skin, 1, 2, 8)
# renders tiles at zoom levels 1 and 2 with the max zoom tile covering 8 units
# Don't like clogging the main directory? Create a new folder and use this instead:
# renderer.render(pla, nodes, skin, 1, 2, 8, saveDir="your_folder_name/")
```