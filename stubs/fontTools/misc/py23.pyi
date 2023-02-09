import math as _math
from io import BytesIO as BytesIO
from io import StringIO as UnicodeIO
from types import SimpleNamespace as SimpleNamespace

from .textTools import Tag as Tag
from .textTools import bytechr as bytechr
from .textTools import byteord as byteord
from .textTools import bytesjoin as bytesjoin
from .textTools import strjoin as strjoin
from .textTools import tobytes as tobytes
from .textTools import tostr as tostr

class Py23Error(NotImplementedError): ...

RecursionError = RecursionError
StringIO = UnicodeIO
basestring = str
isclose = _math.isclose
isfinite = _math.isfinite
open = open
range = range
round = round
round3 = round
unichr = chr
unicode = str
zip = zip
tounicode = tostr

def xrange(*args, **kwargs) -> None: ...
