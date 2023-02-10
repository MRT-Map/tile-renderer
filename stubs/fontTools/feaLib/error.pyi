from _typeshed import Incomplete

class FeatureLibError(Exception):
    location: Incomplete
    def __init__(self, message, location) -> None: ...

class IncludedFeaNotFound(FeatureLibError): ...
