from importlib import metadata

import toml

import renderer.math_utils
import renderer.types
import renderer.validate
from renderer.merge_tiles import merge_tiles
from renderer.render import render
from renderer.types import *

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    try:
        __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "unknown"
