from _typeshed import Incomplete

class VoltLibError(Exception):
    location: Incomplete
    def __init__(self, message, location) -> None: ...
