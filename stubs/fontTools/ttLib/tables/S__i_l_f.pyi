from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.fixedTools import floatToFixedToStr as floatToFixedToStr
from fontTools.misc.textTools import byteord as byteord
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable
from . import grUtils as grUtils

Silf_hdr_format: str
Silf_hdr_format_3: str
Silf_part1_format_v3: str
Silf_part1_format: str
Silf_justify_format: str
Silf_part2_format: str
Silf_pseudomap_format: str
Silf_pseudomap_format_h: str
Silf_classmap_format: str
Silf_lookupclass_format: str
Silf_lookuppair_format: str
Silf_pass_format: str
aCode_info: Incomplete
aCode_map: Incomplete

def disassemble(aCode): ...

instre: Incomplete

def assemble(instrs): ...
def writecode(tag, writer, instrs) -> None: ...
def readcode(content): ...

attrs_info: Incomplete
attrs_passindexes: Incomplete
attrs_contexts: Incomplete
attrs_attributes: Incomplete
pass_attrs_info: Incomplete
pass_attrs_fsm: Incomplete

def writesimple(tag, self, writer, *attrkeys) -> None: ...
def getSimple(self, attrs, *attr_list) -> None: ...
def content_string(contents): ...
def wrapline(writer, dat, length: int = ...) -> None: ...

class _Object: ...

class table_S__i_l_f(DefaultTable.DefaultTable):
    silfs: Incomplete
    def __init__(self, tag: Incomplete | None = ...) -> None: ...
    version: Incomplete
    numSilf: Incomplete
    scheme: int
    compilerVersion: int
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

class Silf:
    passes: Incomplete
    scriptTags: Incomplete
    critFeatures: Incomplete
    jLevels: Incomplete
    pMap: Incomplete
    def __init__(self) -> None: ...
    ruleVersion: Incomplete
    oPasses: Incomplete
    classes: Incomplete
    def decompile(self, data, ttFont, version: float = ...) -> None: ...
    numPasses: Incomplete
    numJLevels: Incomplete
    numCritFeatures: Incomplete
    passOffset: Incomplete
    pseudosOffset: Incomplete
    def compile(self, ttFont, version: float = ...): ...
    def toXML(self, writer, ttFont, version: float = ...) -> None: ...
    def fromXML(self, name, attrs, content, ttFont, version: float = ...) -> None: ...

class Classes:
    linear: Incomplete
    nonLinear: Incomplete
    def __init__(self) -> None: ...
    def decompile(self, data, ttFont, version: float = ...) -> None: ...
    numClass: Incomplete
    numLinear: Incomplete
    def compile(self, ttFont, version: float = ...): ...
    def toXML(self, writer, ttFont, version: float = ...) -> None: ...
    def fromXML(self, name, attrs, content, ttFont, version: float = ...) -> None: ...

class Pass:
    colMap: Incomplete
    rules: Incomplete
    rulePreContexts: Incomplete
    ruleSortKeys: Incomplete
    ruleConstraints: Incomplete
    passConstraints: bytes
    actions: Incomplete
    stateTrans: Incomplete
    startStates: Incomplete
    def __init__(self) -> None: ...
    def decompile(self, data, ttFont, version: float = ...) -> None: ...
    numRules: Incomplete
    fsmOffset: Incomplete
    pcCode: Incomplete
    rcCode: Incomplete
    aCode: Incomplete
    oDebug: int
    def compile(self, ttFont, base, version: float = ...): ...
    def toXML(self, writer, ttFont, version: float = ...): ...
    def fromXML(self, name, attrs, content, ttFont, version: float = ...) -> None: ...
