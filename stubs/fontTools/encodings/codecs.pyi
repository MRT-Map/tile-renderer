import codecs

from _typeshed import Incomplete

class ExtendCodec(codecs.Codec):
    name: Incomplete
    base_encoding: Incomplete
    mapping: Incomplete
    reverse: Incomplete
    max_len: Incomplete
    info: Incomplete
    def __init__(self, name, base_encoding, mapping) -> None: ...
    def encode(self, input, errors: str = ...): ...
    def decode(self, input, errors: str = ...): ...
    def error(self, e): ...

def search_function(name): ...
