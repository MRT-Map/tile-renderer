# tile-renderer

[![Build Status](https://travis-ci.com/MRT-Map/tile-renderer.svg?branch=main)](https://travis-ci.com/MRT-Map/tile-renderer)
[![Documentation Status](https://readthedocs.org/projects/tile-renderer/badge/?version=latest)](https://tile-renderer.readthedocs.io/en/latest/?badge=latest)
[![PyPi Version](https://img.shields.io/pypi/v/tile-renderer.svg)](https://pypi.org/project/tile-renderer/)
![Github Version](https://img.shields.io/github/v/release/MRT-Map/tile-renderer)
[![Python Versions](https://img.shields.io/pypi/pyversions/tile-renderer.svg)](https://pypi.org/project/tile-renderer/)
[![License](https://img.shields.io/pypi/l/tile-renderer.svg)](https://pypi.org/project/tile-renderer/)

![GitHub code size](https://img.shields.io/github/languages/code-size/MRT-Map/tile-renderer)
![GitHub repo size](https://img.shields.io/github/repo-size/MRT-Map/tile-renderer)
![GitHub last commit](https://img.shields.io/github/last-commit/MRT-Map/tile-renderer)
![GitHub Release Date](https://img.shields.io/github/release-date/MRT-Map/tile-renderer)
![Lines of code](https://img.shields.io/tokei/lines/github/MRT-Map/tile-renderer)
[![codecov](https://codecov.io/gh/MRT-Map/tile-renderer/branch/main/graph/badge.svg?token=VTJ73KYYF0)](https://codecov.io/gh/MRT-Map/tile-renderer)
[![CodeFactor](https://www.codefactor.io/repository/github/mrt-map/tile-renderer/badge)](https://www.codefactor.io/repository/github/mrt-map/tile-renderer)

Leaflet.js streetmap tile renderer, made by 7d

**Note: renderer is complete, but not the skin or the tutorials.**

**Documentation: https://tile-renderer.readthedocs.io/en/latest/**

## Current version: v2.0
* **v2.0 (23/12/21)**
  * "PLA" is no longer defined as "a set of components" but a file type (`.pla`)
    * Components are called... Components
    * Component JSON files have a `.comps.pla` suffix
    * Node JSON files have a `.nodes.pla` suffix
  * The CLI format has changed substantially to follow PEP8 naming conventions
  * The entire codebase has been reformatted to follow PEP8 naming conventions
  * Skins, components and nodes (& their list counterparts) now have their own classes, to make the code cleaner
  * Coords and TileCoords are now NamedTuples
  * `pathlib.Path` is now being used instead of raw strings
  * Ray multiprocessing integration (3.8 and 3.9 only)
  * Text rendering is now separated from the main rendering task
  * Rendering logs will no longer use the same line but rather will output one log per line
  * Builders:
    * Default IDs can now be set
      * PyAutoGUI is now used to automatically write the default ID
    * Commands now start with "."
    * ... and many more I probably forgot lol
  * `internals.internal` is now typed
  * Loggers and texts (for later rendering) now have their own private classes
  * Several functions in `mathtools` (`lines_intersect`, `point_in_poly`, `poly_center`) are now quicker to run (mostly using NumPy)
    * SymPy is no longer a dependency (yey)
  * `misc` no longer exists (`misc.getSkin` is now `Skin.from_name`)
  * `tools` is now split up into 6 files
  * Many functions in `validate` are now in their respective object classes
  * Made the CLI actually work (:P)
* **Past changelogs can be found in https://tile-renderer.readthedocs.io/en/latest/changelog.html**

## Usage (simple)
1. Download or clone this repo; or run `pip install tile-renderer` (For ray functionality do `pip install ray`)
2. Write a node JSON file and a component JSON file. (Tutorial coming soon) Or, use the example files provided in `data`.
3. In your file, run the renderer. Here is an example code:

```python
import renderer  # important!!
import json


def read_file(path):  # extract from JSON as dict
    with open(path, "r") as f:
        data = json.load(f)
        f.close()
        return data
    
nodes = renderer.NodeList(read_file("path_to_your_nodes_file/blah.nodes.pla"))
comps = renderer.ComponentList(read_file("path_to_your_components_file/blah.comps.pla"),
                               read_file("path_to_your_nodes_file/blah.nodes.pla"))

if __name__ == "__main__": renderer.render(comps, nodes, 1, 2, 8)
# renders tiles at zoom levels 1 and 2 with the max zoom tile covering 8 units
# Don't like clogging the main directory? Create a new folder and use this instead:
# if __name__ == "__main__": renderer.render(comps, nodes, 1, 2, 8, save_dir=Path("your_folder_name/"))
# Too slow? Increase the number of processes
# if __name__ == "__main__": renderer.render(comps, nodes, 1, 2, 8, processes=5)
```

<!--
commands for upload in case i forget

python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*
-->
