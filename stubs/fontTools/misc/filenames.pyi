from _typeshed import Incomplete

illegalCharacters: Incomplete
reservedFileNames: Incomplete
maxFileNameLength: int

class NameTranslationError(Exception): ...

def userNameToFileName(
    userName, existing=..., prefix: str = ..., suffix: str = ...
): ...
def handleClash1(userName, existing=..., prefix: str = ..., suffix: str = ...): ...
def handleClash2(existing=..., prefix: str = ..., suffix: str = ...): ...
