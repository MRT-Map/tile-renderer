from io import BytesIO

from _typeshed import Incomplete
from fontTools.misc.macRes import ResourceError as ResourceError
from fontTools.misc.macRes import ResourceReader as ResourceReader

def getSFNTResIndices(path): ...
def openTTFonts(path): ...

class SFNTResourceReader(BytesIO):
    rsrc: Incomplete
    name: Incomplete
    def __init__(self, path, res_name_or_index) -> None: ...
