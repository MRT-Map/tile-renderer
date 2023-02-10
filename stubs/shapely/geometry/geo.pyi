from shapely.errors import GeometryTypeError as GeometryTypeError

from .collection import GeometryCollection as GeometryCollection
from .linestring import LineString as LineString
from .multilinestring import MultiLineString as MultiLineString
from .multipoint import MultiPoint as MultiPoint
from .multipolygon import MultiPolygon as MultiPolygon
from .point import Point as Point
from .polygon import LinearRing as LinearRing
from .polygon import Polygon as Polygon

def box(minx, miny, maxx, maxy, ccw: bool = ...): ...
def shape(context): ...
def mapping(ob): ...
