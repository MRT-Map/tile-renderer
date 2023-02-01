from importlib import metadata

import toml

import renderer.math_utils
import renderer.types

from .merge_tiles import merge_tiles
from .render import *
from .types import *

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    try:
        __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "unknown"
