class Visitor:
    defaultStop: bool
    @classmethod
    def register(celf, clazzes): ...
    @classmethod
    def register_attr(celf, clazzes, attrs): ...
    @classmethod
    def register_attrs(celf, clazzes_attrs): ...
    def visitObject(self, obj, *args, **kwargs) -> None: ...
    def visitAttr(self, obj, attr, value, *args, **kwargs) -> None: ...
    def visitList(self, obj, *args, **kwargs) -> None: ...
    def visitDict(self, obj, *args, **kwargs) -> None: ...
    def visitLeaf(self, obj, *args, **kwargs) -> None: ...
    def visit(self, obj, *args, **kwargs) -> None: ...
