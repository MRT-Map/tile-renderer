from _typeshed import Incomplete
from fontTools.feaLib.error import FeatureLibError as FeatureLibError
from fontTools.feaLib.error import IncludedFeaNotFound as IncludedFeaNotFound
from fontTools.feaLib.location import FeatureLibLocation as FeatureLibLocation
from fontTools.misc import cython as cython

class Lexer:
    NUMBER: str
    HEXADECIMAL: str
    OCTAL: str
    NUMBERS: Incomplete
    FLOAT: str
    STRING: str
    NAME: str
    FILENAME: str
    GLYPHCLASS: str
    CID: str
    SYMBOL: str
    COMMENT: str
    NEWLINE: str
    ANONYMOUS_BLOCK: str
    CHAR_WHITESPACE_: str
    CHAR_NEWLINE_: str
    CHAR_SYMBOL_: str
    CHAR_DIGIT_: str
    CHAR_HEXDIGIT_: str
    CHAR_LETTER_: str
    CHAR_NAME_START_: Incomplete
    CHAR_NAME_CONTINUATION_: Incomplete
    RE_GLYPHCLASS: Incomplete
    MODE_NORMAL_: str
    MODE_FILENAME_: str
    filename_: Incomplete
    line_: int
    pos_: int
    line_start_: int
    text_: Incomplete
    text_length_: Incomplete
    mode_: Incomplete
    def __init__(self, text, filename) -> None: ...
    def __iter__(self): ...
    def next(self): ...
    def __next__(self): ...
    def location_(self): ...
    def next_(self): ...
    def scan_over_(self, valid) -> None: ...
    def scan_until_(self, stop_at) -> None: ...
    def scan_anonymous_block(self, tag): ...

class IncludingLexer:
    lexers_: Incomplete
    featurefilepath: Incomplete
    includeDir: Incomplete
    def __init__(self, featurefile, *, includeDir: Incomplete | None = ...) -> None: ...
    def __iter__(self): ...
    def next(self): ...
    def __next__(self): ...
    @staticmethod
    def make_lexer_(file_or_path): ...
    def scan_anonymous_block(self, tag): ...

class NonIncludingLexer(IncludingLexer):
    def __next__(self): ...
