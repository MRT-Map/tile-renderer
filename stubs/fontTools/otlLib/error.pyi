from _typeshed import Incomplete

class OpenTypeLibError(Exception):
    location: Incomplete
    def __init__(self, message, location) -> None: ...
