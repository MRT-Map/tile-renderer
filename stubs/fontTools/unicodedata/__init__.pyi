from unicodedata import *

from _typeshed import Incomplete
from fontTools.misc.textTools import byteord as byteord
from fontTools.misc.textTools import tostr as tostr
from unicodedata2 import *

from . import Blocks as Blocks
from . import OTTags as OTTags
from . import ScriptExtensions as ScriptExtensions
from . import Scripts as Scripts

def script(char): ...
def script_extension(char): ...
def script_name(code, default=...): ...
def script_code(script_name, default=...): ...

RTL_SCRIPTS: Incomplete

def script_horizontal_direction(script_code, default=...): ...
def block(char): ...
def ot_tags_from_script(script_code): ...
def ot_tag_to_script(tag): ...
