from fontTools.misc.textTools import Tag as Tag
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import strjoin as strjoin

def getMacCreatorAndType(path): ...
def setMacCreatorAndType(path, fileCreator, fileType) -> None: ...