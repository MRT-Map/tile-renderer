# tile-renderer

[![Build Status](https://travis-ci.com/MRT-Map/tile-renderer.svg?branch=main)](https://travis-ci.com/MRT-Map/tile-renderer)
[![Documentation Status](https://readthedocs.org/projects/tile-renderer/badge/?version=latest)](https://tile-renderer.readthedocs.io/en/latest/?badge=latest)
[![Version](https://img.shields.io/pypi/v/tile-renderer.svg)](https://pypi.org/project/tile-renderer/)
[![License](https://img.shields.io/pypi/l/tile-renderer.svg)](https://pypi.org/project/tile-renderer/)
[![Versions](https://img.shields.io/pypi/pyversions/tile-renderer.svg)](https://pypi.org/project/tile-renderer/)

Leaflet.js streetmap tile renderer, made by 7d

**Note: renderer is complete, but not the skin or the tutorials.**

**Documentation: https://tile-renderer.readthedocs.io/en/latest/**

## Current version: v1.2
* **v1.2 ()**
  * `renderer.render()` now ignores PLAs if their type is not specified in the skin Json
  * Hollows are now supported in areas
  * New function, `renderer.validate.vGeoJson()`
    * `renderer.validate.vCoords()` now supports lists along with tuples
  * The renderer now has a CLI, to show the help page do `python -m renderer -h`
  * `renderer.render()` now supports float maxZoomRanges
  * New functions: `renderer.tools.plaJson.toGeoJson()` and `renderer.tools.geoJson.toNodePlaJson()`
    * these are for translating our custom format of storing geographical format to geoJson
    * (btw why we're not using geoJson is because its harder to store nodes)
* **Past changelogs can be found in https://tile-renderer.readthedocs.io/en/latest/changelog.html**

## Usage (simple)
1. Download or clone this repo; or run `pip install tile-renderer`
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

if __name__ == "__main__": renderer.render(pla, nodes, skin, 1, 2, 8)
# renders tiles at zoom levels 1 and 2 with the max zoom tile covering 8 units
# Don't like clogging the main directory? Create a new folder and use this instead:
# if __name__ == "__main__": renderer.render(pla, nodes, skin, 1, 2, 8, saveDir="your_folder_name/")
# Too slow? Increase the number of processes
# if __name__ == "__main__": renderer.render(pla, nodes, skin, 1, 2, 8, processes=5)
```

<!--
commands for upload in case i forget

py -m build
twine upload dist/*
-->