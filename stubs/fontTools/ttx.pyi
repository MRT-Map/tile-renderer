from _typeshed import Incomplete
from fontTools.misc.cliTools import makeOutputFileName as makeOutputFileName
from fontTools.misc.loggingTools import Timer as Timer
from fontTools.misc.macCreatorType import getMacCreatorAndType as getMacCreatorAndType
from fontTools.misc.textTools import Tag as Tag
from fontTools.misc.textTools import tostr as tostr
from fontTools.misc.timeTools import timestampSinceEpoch as timestampSinceEpoch
from fontTools.ttLib import TTFont as TTFont
from fontTools.ttLib import TTLibError as TTLibError
from fontTools.unicode import setUnicodeData as setUnicodeData

log: Incomplete
opentypeheaderRE: Incomplete

class Options:
    listTables: bool
    outputDir: Incomplete
    outputFile: Incomplete
    overWrite: bool
    verbose: bool
    quiet: bool
    splitTables: bool
    splitGlyphs: bool
    disassembleInstructions: bool
    mergeFile: Incomplete
    recalcBBoxes: bool
    ignoreDecompileErrors: bool
    bitmapGlyphDataFormat: str
    unicodedata: Incomplete
    newlinestr: str
    recalcTimestamp: Incomplete
    flavor: Incomplete
    useZopfli: bool
    onlyTables: Incomplete
    skipTables: Incomplete
    fontNumber: int
    logLevel: Incomplete
    def __init__(self, rawOptions, numFiles) -> None: ...

def ttList(input, output, options) -> None: ...
def ttDump(input, output, options) -> None: ...
def ttCompile(input, output, options) -> None: ...
def guessFileType(fileName): ...
def parseOptions(args): ...
def process(jobs, options) -> None: ...
def main(args: Incomplete | None = ...) -> None: ...
