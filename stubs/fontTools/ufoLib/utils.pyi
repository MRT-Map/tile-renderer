from _typeshed import Incomplete

numberTypes: Incomplete

def deprecated(msg: str = ...): ...

class _VersionTupleEnumMixin:
    @property
    def major(self): ...
    @property
    def minor(self): ...
    @classmethod
    def default(cls): ...
    @classmethod
    def supported_versions(cls): ...
