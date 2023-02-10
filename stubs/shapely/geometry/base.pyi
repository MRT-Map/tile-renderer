import shapely
from _typeshed import Incomplete
from shapely.constructive import BufferCapStyle as BufferCapStyle
from shapely.constructive import BufferJoinStyle as BufferJoinStyle
from shapely.coords import CoordinateSequence as CoordinateSequence
from shapely.errors import GeometryTypeError as GeometryTypeError
from shapely.errors import GEOSException as GEOSException
from shapely.errors import ShapelyDeprecationWarning as ShapelyDeprecationWarning

GEOMETRY_TYPES: Incomplete

def geom_factory(g, parent: Incomplete | None = ...): ...
def dump_coords(geom): ...

class CAP_STYLE:
    round: Incomplete
    flat: Incomplete
    square: Incomplete

class JOIN_STYLE:
    round: Incomplete
    mitre: Incomplete
    bevel: Incomplete

class BaseGeometry(shapely.Geometry):
    def __new__(self): ...
    def __bool__(self) -> bool: ...
    def __nonzero__(self): ...
    def __format__(self, format_spec) -> str: ...
    def __reduce__(self): ...
    def __and__(self, other): ...
    def __or__(self, other): ...
    def __sub__(self, other): ...
    def __xor__(self, other): ...
    @property
    def coords(self): ...
    @property
    def xy(self) -> None: ...
    @property
    def __geo_interface__(self) -> None: ...
    def geometryType(self): ...
    @property
    def type(self): ...
    @property
    def wkt(self): ...
    @property
    def wkb(self): ...
    @property
    def wkb_hex(self): ...
    def svg(self, scale_factor: float = ..., **kwargs) -> None: ...
    @property
    def geom_type(self): ...
    @property
    def area(self): ...
    def distance(self, other): ...
    def hausdorff_distance(self, other): ...
    @property
    def length(self): ...
    @property
    def minimum_clearance(self): ...
    @property
    def boundary(self): ...
    @property
    def bounds(self): ...
    @property
    def centroid(self): ...
    def point_on_surface(self): ...
    def representative_point(self): ...
    @property
    def convex_hull(self): ...
    @property
    def envelope(self): ...
    @property
    def oriented_envelope(self): ...
    @property
    def minimum_rotated_rectangle(self): ...
    def buffer(
        self,
        distance,
        quad_segs: int = ...,
        cap_style: str = ...,
        join_style: str = ...,
        mitre_limit: float = ...,
        single_sided: bool = ...,
        **kwargs
    ): ...
    def simplify(self, tolerance, preserve_topology: bool = ...): ...
    def normalize(self): ...
    def difference(self, other, grid_size: Incomplete | None = ...): ...
    def intersection(self, other, grid_size: Incomplete | None = ...): ...
    def symmetric_difference(self, other, grid_size: Incomplete | None = ...): ...
    def union(self, other, grid_size: Incomplete | None = ...): ...
    @property
    def has_z(self): ...
    @property
    def is_empty(self): ...
    @property
    def is_ring(self): ...
    @property
    def is_closed(self): ...
    @property
    def is_simple(self): ...
    @property
    def is_valid(self): ...
    def relate(self, other): ...
    def covers(self, other): ...
    def covered_by(self, other): ...
    def contains(self, other): ...
    def contains_properly(self, other): ...
    def crosses(self, other): ...
    def disjoint(self, other): ...
    def equals(self, other): ...
    def intersects(self, other): ...
    def overlaps(self, other): ...
    def touches(self, other): ...
    def within(self, other): ...
    def dwithin(self, other, distance): ...
    def equals_exact(self, other, tolerance): ...
    def almost_equals(self, other, decimal: int = ...): ...
    def relate_pattern(self, other, pattern): ...
    def line_locate_point(self, other, normalized: bool = ...): ...
    def project(self, other, normalized: bool = ...): ...
    def line_interpolate_point(self, distance, normalized: bool = ...): ...
    def interpolate(self, distance, normalized: bool = ...): ...
    def segmentize(self, max_segment_length): ...
    def reverse(self): ...

class BaseMultipartGeometry(BaseGeometry):
    @property
    def coords(self) -> None: ...
    @property
    def geoms(self): ...
    def __bool__(self) -> bool: ...
    def svg(self, scale_factor: float = ..., color: Incomplete | None = ...): ...  # type: ignore

class GeometrySequence:
    def __init__(self, parent) -> None: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def __getitem__(self, key): ...

class EmptyGeometry(BaseGeometry):
    def __new__(self): ...
