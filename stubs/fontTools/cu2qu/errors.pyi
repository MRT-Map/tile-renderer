from _typeshed import Incomplete

class Error(Exception): ...

class ApproxNotFoundError(Error):
    curve: Incomplete
    def __init__(self, curve) -> None: ...

class UnequalZipLengthsError(Error): ...

class IncompatibleGlyphsError(Error):
    glyphs: Incomplete
    combined_name: Incomplete
    def __init__(self, glyphs) -> None: ...

class IncompatibleSegmentNumberError(IncompatibleGlyphsError): ...

class IncompatibleSegmentTypesError(IncompatibleGlyphsError):
    segments: Incomplete
    def __init__(self, glyphs, segments) -> None: ...

class IncompatibleFontsError(Error):
    glyph_errors: Incomplete
    def __init__(self, glyph_errors) -> None: ...
