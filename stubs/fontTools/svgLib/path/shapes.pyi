from _typeshed import Incomplete

class PathBuilder:
    paths: Incomplete
    transforms: Incomplete
    def __init__(self) -> None: ...
    def M(self, x, y) -> None: ...
    def m(self, x, y) -> None: ...
    def A(self, rx, ry, x, y, large_arc: int = ...) -> None: ...
    def a(self, rx, ry, x, y, large_arc: int = ...) -> None: ...
    def H(self, x) -> None: ...
    def h(self, x) -> None: ...
    def V(self, y) -> None: ...
    def v(self, y) -> None: ...
    def L(self, x, y) -> None: ...
    def l(self, x, y) -> None: ...
    def add_path_from_element(self, el): ...
