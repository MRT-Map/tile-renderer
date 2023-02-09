from _typeshed import Incomplete
from fontTools.misc.loggingTools import deprecateFunction as deprecateFunction
from fontTools.ttLib.ttCollection import TTCollection as TTCollection
from fontTools.ttLib.ttFont import *

log: Incomplete  # type: ignore

class TTLibError(Exception): ...

def debugmsg(msg) -> None: ...
