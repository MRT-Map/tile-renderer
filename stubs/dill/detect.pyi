from _typeshed import Incomplete

from .logger import trace as trace

def getmodule(object, _filename: Incomplete | None = ..., force: bool = ...): ...
def outermost(func): ...
def nestedcode(func, recurse: bool = ...): ...
def code(func): ...
def referrednested(func, recurse: bool = ...): ...
def freevars(func): ...
def nestedglobals(func, recurse: bool = ...): ...
def referredglobals(func, recurse: bool = ..., builtin: bool = ...): ...
def globalvars(func, recurse: bool = ..., builtin: bool = ...): ...
def varnames(func): ...
def baditems(obj, exact: bool = ..., safe: bool = ...): ...
def badobjects(obj, depth: int = ..., exact: bool = ..., safe: bool = ...): ...
def badtypes(obj, depth: int = ..., exact: bool = ..., safe: bool = ...): ...
def errors(obj, depth: int = ..., exact: bool = ..., safe: bool = ...): ...
