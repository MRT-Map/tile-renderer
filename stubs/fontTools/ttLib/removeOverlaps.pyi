from typing import Iterable, Optional

from fontTools.ttLib import ttFont

class RemoveOverlapsError(Exception): ...

def removeOverlaps(
    font: ttFont.TTFont,
    glyphNames: Optional[Iterable[str]] = ...,
    removeHinting: bool = ...,
    ignoreErrors: bool = ...,
) -> None: ...
