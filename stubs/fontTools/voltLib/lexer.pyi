from _typeshed import Incomplete
from fontTools.voltLib.error import VoltLibError as VoltLibError

class Lexer:
    NUMBER: str
    STRING: str
    NAME: str
    NEWLINE: str
    CHAR_WHITESPACE_: str
    CHAR_NEWLINE_: str
    CHAR_DIGIT_: str
    CHAR_UC_LETTER_: str
    CHAR_LC_LETTER_: str
    CHAR_UNDERSCORE_: str
    CHAR_PERIOD_: str
    CHAR_NAME_START_: Incomplete
    CHAR_NAME_CONTINUATION_: Incomplete
    filename_: Incomplete
    line_: int
    pos_: int
    line_start_: int
    text_: Incomplete
    text_length_: Incomplete
    def __init__(self, text, filename) -> None: ...
    def __iter__(self): ...
    def next(self): ...
    def __next__(self): ...
    def location_(self): ...
    def next_(self): ...
    def scan_over_(self, valid) -> None: ...
    def scan_until_(self, stop_at) -> None: ...
