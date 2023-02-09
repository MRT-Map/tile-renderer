from typing import Callable, Deque, Iterable, List, Optional, Tuple

from .otBase import BaseTable

class SubTablePath(Tuple[BaseTable.SubTableEntry, ...]): ...

AddToFrontierFn = Callable[[Deque[SubTablePath], List[SubTablePath]], None]

def dfs_base_table(
    root: BaseTable,
    root_accessor: Optional[str] = ...,
    skip_root: bool = ...,
    predicate: Optional[Callable[[SubTablePath], bool]] = ...,
) -> Iterable[SubTablePath]: ...
def bfs_base_table(
    root: BaseTable,
    root_accessor: Optional[str] = ...,
    skip_root: bool = ...,
    predicate: Optional[Callable[[SubTablePath], bool]] = ...,
) -> Iterable[SubTablePath]: ...
