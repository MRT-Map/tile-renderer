from unittest import TestCase as _TestCase

from _typeshed import Incomplete
from fontTools.config import Config as Config
from fontTools.misc.textTools import tobytes as tobytes
from fontTools.misc.xmlWriter import XMLWriter as XMLWriter

def parseXML(xmlSnippet): ...
def parseXmlInto(font, parseInto, xmlSnippet): ...

class FakeFont:
    glyphOrder_: Incomplete
    reverseGlyphOrderDict_: Incomplete
    lazy: bool
    tables: Incomplete
    cfg: Incomplete
    def __init__(self, glyphs) -> None: ...
    def __getitem__(self, tag): ...
    def __setitem__(self, tag, table) -> None: ...
    def get(self, tag, default: Incomplete | None = ...): ...
    def getGlyphID(self, name): ...
    def getGlyphIDMany(self, lst): ...
    def getGlyphName(self, glyphID): ...
    def getGlyphNameMany(self, lst): ...
    def getGlyphOrder(self): ...
    def getReverseGlyphMap(self): ...
    def getGlyphNames(self): ...

class TestXMLReader_:
    parser: Incomplete
    root: Incomplete
    stack: Incomplete
    def __init__(self) -> None: ...
    def startElement_(self, name, attrs) -> None: ...
    def endElement_(self, name) -> None: ...
    def addCharacterData_(self, data) -> None: ...

def makeXMLWriter(newlinestr: str = ...): ...
def getXML(func, ttFont: Incomplete | None = ...): ...
def stripVariableItemsFromTTX(
    string: str,
    ttLibVersion: bool = ...,
    checkSumAdjustment: bool = ...,
    modified: bool = ...,
    created: bool = ...,
    sfntVersion: bool = ...,
) -> str: ...

class MockFont:
    lazy: bool
    def __init__(self) -> None: ...
    def getGlyphID(self, glyph): ...
    def getReverseGlyphMap(self): ...
    def getGlyphName(self, gid): ...
    def getGlyphOrder(self): ...

class TestCase(_TestCase):
    assertRaisesRegex: Incomplete
    def __init__(self, methodName) -> None: ...

class DataFilesHandler(TestCase):
    tempdir: Incomplete
    num_tempfiles: int
    def setUp(self) -> None: ...
    def tearDown(self) -> None: ...
    def getpath(self, testfile): ...
    def temp_dir(self) -> None: ...
    def temp_font(self, font_path, file_name): ...
