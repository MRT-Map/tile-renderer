from importlib import metadata

import toml

import renderer.internals
import renderer.mathtools
import renderer.types
import renderer.validate
from renderer.base import merge_tiles, render
from renderer.objects.components import *
from renderer.objects.nodes import *
from renderer.objects.skin import *
from renderer.objects.skinbuilder import *
from renderer.objects.zoom_params import *

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    try:
        __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "unknown"
