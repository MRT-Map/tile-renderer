from _typeshed import Incomplete

from .table_builder import TableUnbuilder as TableUnbuilder

def unbuildColrV1(layerList, baseGlyphList): ...

class LayerListUnbuilder:
    layers: Incomplete
    tableUnbuilder: Incomplete
    def __init__(self, layers) -> None: ...
    def unbuildPaint(self, paint): ...
