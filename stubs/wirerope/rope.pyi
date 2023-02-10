from _typeshed import Incomplete

class RopeCore:
    callable: Incomplete
    rope: Incomplete
    def __init__(self, callable, rope) -> None: ...
    @property
    def wire_class(self): ...

class MethodRopeMixin:
    def __init__(self, *args, **kwargs) -> None: ...
    wire_name: Incomplete
    def __set_name__(self, owner, name) -> None: ...
    def __get__(self, obj, type: Incomplete | None = ...): ...

class PropertyRopeMixin:
    def __init__(self, *args, **kwargs) -> None: ...
    wire_name: Incomplete
    def __set_name__(self, owner, name) -> None: ...
    def __get__(self, obj, type: Incomplete | None = ...): ...

class FunctionRopeMixin:
    def __init__(self, *args, **kwargs) -> None: ...
    def __getattr__(self, name): ...

class CallableRopeMixin:
    def __init__(self, *args, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs): ...

class WireRope:
    wire_class: Incomplete
    method_rope: Incomplete
    property_rope: Incomplete
    function_rope: Incomplete
    callable_function_rope: Incomplete
    def __init__(
        self,
        wire_class,
        core_class=...,
        wraps: bool = ...,
        rope_args: Incomplete | None = ...,
    ) -> None: ...
    def __call__(self, function): ...
