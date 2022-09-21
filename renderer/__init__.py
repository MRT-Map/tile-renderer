from renderer.base import merge_tiles, render
import renderer.mathtools
import renderer.validate
import renderer.types
from renderer.objects.nodes import *
from renderer.objects.components import *
from renderer.objects.skin import *
from renderer.objects.skinbuilder import *
from renderer.objects.zoom_params import *
import renderer.internals

from importlib import metadata
import toml

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    try:
        __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "unknown"
