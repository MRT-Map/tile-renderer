from _typeshed import Incomplete
from shapely.geometry.base import BaseGeometry as BaseGeometry
from shapely.geometry.base import BaseMultipartGeometry as BaseMultipartGeometry

class GeometryCollection(BaseMultipartGeometry):
    def __new__(self, geoms: Incomplete | None = ...): ...
    @property
    def __geo_interface__(self): ...
