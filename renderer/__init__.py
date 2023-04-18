from importlib import metadata

import toml

import renderer.math_utils
import renderer.merge_tiles
import renderer.misc_types
import renderer.pla1to2
import renderer.skin_type

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    try:
        __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "unknown"
