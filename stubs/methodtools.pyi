from _typeshed import Incomplete
from wirerope import Wire

class _LruCacheWire(Wire):
    cache_clear: Incomplete
    cache_info: Incomplete
    def __init__(self, rope, *args, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs): ...

def lru_cache(*args, **kwargs): ...
