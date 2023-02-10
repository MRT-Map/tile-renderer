from _typeshed import Incomplete
from fontTools.misc.sstruct import calcsize as calcsize
from fontTools.misc.sstruct import unpack as unpack
from fontTools.misc.sstruct import unpack2 as unpack2

SIZES_FORMAT: str
SIZES_SIZE: Incomplete
FIXED_FORMAT: str
HEADER_FORMAT1: Incomplete
HEADER_FORMAT2: Incomplete
HEADER_FORMAT3: Incomplete
HEADER_FORMAT4: Incomplete
HEADER_SIZE1: Incomplete
HEADER_SIZE2: Incomplete
HEADER_SIZE3: Incomplete
HEADER_SIZE4: Incomplete
LIG_KERN_COMMAND: str
BASE_PARAMS: Incomplete
MATHSY_PARAMS: Incomplete
MATHEX_PARAMS: Incomplete
VANILLA: int
MATHSY: int
MATHEX: int
UNREACHABLE: int
PASSTHROUGH: int
ACCESSABLE: int
NO_TAG: int
LIG_TAG: int
LIST_TAG: int
EXT_TAG: int
STOP_FLAG: int
KERN_FLAG: int

class TFMException(Exception):
    def __init__(self, message) -> None: ...

class TFM:
    def __init__(self, file) -> None: ...
