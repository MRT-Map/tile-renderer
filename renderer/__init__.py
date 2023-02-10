from importlib import metadata

import toml

import renderer.math_utils
import renderer.misc_types

from .merge_tiles import *
from .misc_types import *
from .render import *

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    try:
        __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "unknown"
