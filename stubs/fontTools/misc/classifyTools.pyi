class Classifier:
    def __init__(self, sort: bool = ...) -> None: ...
    def add(self, set_of_things) -> None: ...
    def update(self, list_of_sets) -> None: ...
    def getThings(self): ...
    def getMapping(self): ...
    def getClasses(self): ...

def classify(list_of_sets, sort: bool = ...): ...
