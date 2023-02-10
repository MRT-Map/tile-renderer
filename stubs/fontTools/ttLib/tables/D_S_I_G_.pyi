from _typeshed import Incomplete
from fontTools.misc import sstruct as sstruct
from fontTools.misc.textTools import bytesjoin as bytesjoin
from fontTools.misc.textTools import safeEval as safeEval
from fontTools.misc.textTools import strjoin as strjoin
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.textTools import tostr as tostr

from . import DefaultTable as DefaultTable

DSIG_HeaderFormat: str
DSIG_SignatureFormat: str
DSIG_SignatureBlockFormat: str

class table_D_S_I_G_(DefaultTable.DefaultTable):
    signatureRecords: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, xmlWriter, ttFont) -> None: ...
    ulVersion: Incomplete
    usNumSigs: Incomplete
    usFlag: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...

pem_spam: Incomplete

def b64encode(b): ...

class SignatureRecord:
    def toXML(self, writer, ttFont) -> None: ...
    ulFormat: Incomplete
    usReserved1: Incomplete
    usReserved2: Incomplete
    pkcs7: Incomplete
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
