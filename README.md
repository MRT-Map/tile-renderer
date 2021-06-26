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

## Current version: v1.3
* **v1.3 ()**
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

python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*
-->
