from _typeshed import Incomplete
from fontTools.misc.textTools import safeEval as safeEval

from . import DefaultTable as DefaultTable

class table__c_v_t(DefaultTable.DefaultTable):
    values: Incomplete
    def decompile(self, data, ttFont) -> None: ...
    def compile(self, ttFont): ...
    def toXML(self, writer, ttFont) -> None: ...
    def fromXML(self, name, attrs, content, ttFont) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index): ...
    def __setitem__(self, index, value) -> None: ...
    def __delitem__(self, index) -> None: ...
