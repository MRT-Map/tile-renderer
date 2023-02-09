from _typeshed import Incomplete
from fontTools.encodings.StandardEncoding import StandardEncoding as StandardEncoding

class ps_object:
    literal: int
    access: int
    value: Incomplete
    type: Incomplete
    def __init__(self, value) -> None: ...

class ps_operator(ps_object):
    literal: int
    name: Incomplete
    function: Incomplete
    type: Incomplete
    def __init__(self, name, function) -> None: ...

class ps_procedure(ps_object):
    literal: int

class ps_name(ps_object):
    literal: int

class ps_literal(ps_object): ...
class ps_array(ps_object): ...
class ps_font(ps_object): ...
class ps_file(ps_object): ...
class ps_dict(ps_object): ...

class ps_mark(ps_object):
    value: str
    type: Incomplete
    def __init__(self) -> None: ...

class ps_procmark(ps_object):
    value: str
    type: Incomplete
    def __init__(self) -> None: ...

class ps_null(ps_object):
    type: Incomplete
    def __init__(self) -> None: ...

class ps_boolean(ps_object): ...
class ps_string(ps_object): ...
class ps_integer(ps_object): ...
class ps_real(ps_object): ...

class PSOperators:
    def ps_def(self) -> None: ...
    def ps_bind(self) -> None: ...
    def proc_bind(self, proc) -> None: ...
    def ps_exch(self) -> None: ...
    def ps_dup(self) -> None: ...
    def ps_exec(self) -> None: ...
    def ps_count(self) -> None: ...
    def ps_eq(self) -> None: ...
    def ps_ne(self) -> None: ...
    def ps_cvx(self) -> None: ...
    def ps_matrix(self) -> None: ...
    def ps_string(self) -> None: ...
    def ps_type(self) -> None: ...
    def ps_store(self) -> None: ...
    def ps_where(self) -> None: ...
    def ps_systemdict(self) -> None: ...
    def ps_userdict(self) -> None: ...
    def ps_currentdict(self) -> None: ...
    def ps_currentfile(self) -> None: ...
    def ps_eexec(self) -> None: ...
    def ps_closefile(self) -> None: ...
    def ps_cleartomark(self) -> None: ...
    def ps_readstring(self, ps_boolean=..., len=...) -> None: ...
    def ps_known(self) -> None: ...
    def ps_if(self) -> None: ...
    def ps_ifelse(self) -> None: ...
    def ps_readonly(self) -> None: ...
    def ps_executeonly(self) -> None: ...
    def ps_noaccess(self) -> None: ...
    def ps_not(self) -> None: ...
    def ps_print(self) -> None: ...
    def ps_anchorsearch(self) -> None: ...
    def ps_array(self) -> None: ...
    def ps_astore(self) -> None: ...
    def ps_load(self) -> None: ...
    def ps_put(self) -> None: ...
    def ps_get(self) -> None: ...
    def ps_getinterval(self) -> None: ...
    def ps_putinterval(self) -> None: ...
    def ps_cvn(self) -> None: ...
    def ps_index(self) -> None: ...
    def ps_for(self) -> None: ...
    def ps_forall(self) -> None: ...
    def ps_definefont(self) -> None: ...
    def ps_findfont(self) -> None: ...
    def ps_pop(self) -> None: ...
    def ps_dict(self) -> None: ...
    def ps_begin(self) -> None: ...
    def ps_end(self) -> None: ...

notdef: str
ps_StandardEncoding: Incomplete
