from _typeshed import Incomplete
from shapely import GeometryCollection as GeometryCollection
from shapely import LineString as LineString
from shapely import Point as Point
from shapely import Polygon as Polygon
from shapely.errors import UnsupportedGEOSVersionError as UnsupportedGEOSVersionError
from shapely.testing import assert_geometries_equal as assert_geometries_equal

from .common import all_types as all_types
from .common import empty_point as empty_point
from .common import empty_point_z as empty_point_z
from .common import point as point
from .common import point_z as point_z

POINT11_WKB: Incomplete
NAN: Incomplete
POINT_NAN_WKB: Incomplete
POINTZ_NAN_WKB: Incomplete
MULTIPOINT_NAN_WKB: Incomplete
MULTIPOINTZ_NAN_WKB: Incomplete
GEOMETRYCOLLECTION_NAN_WKB: Incomplete
GEOMETRYCOLLECTIONZ_NAN_WKB: Incomplete
NESTED_COLLECTION_NAN_WKB: Incomplete
NESTED_COLLECTIONZ_NAN_WKB: Incomplete
INVALID_WKB: str
GEOJSON_GEOMETRY: Incomplete
GEOJSON_FEATURE: Incomplete
GEOJSON_FEATURECOLECTION: Incomplete
GEOJSON_GEOMETRY_EXPECTED: Incomplete
GEOJSON_COLLECTION_EXPECTED: Incomplete

def test_from_wkt() -> None: ...
def test_from_wkt_none() -> None: ...
def test_from_wkt_exceptions() -> None: ...
def test_from_wkt_warn_on_invalid() -> None: ...
def test_from_wkb_ignore_on_invalid() -> None: ...
def test_from_wkt_on_invalid_unsupported_option() -> None: ...
def test_from_wkt_all_types(geom) -> None: ...
def test_from_wkt_empty(wkt) -> None: ...
def test_from_wkb() -> None: ...
def test_from_wkb_hex() -> None: ...
def test_from_wkb_none() -> None: ...
def test_from_wkb_exceptions() -> None: ...
def test_from_wkb_warn_on_invalid_warn() -> None: ...
def test_from_wkb_ignore_on_invalid_ignore() -> None: ...
def test_from_wkb_on_invalid_unsupported_option() -> None: ...
def test_from_wkb_all_types(geom, use_hex, byte_order) -> None: ...
def test_from_wkb_empty(geom) -> None: ...
def test_to_wkt() -> None: ...
def test_to_wkt_3D() -> None: ...
def test_to_wkt_none() -> None: ...
def test_to_wkt_exceptions() -> None: ...
def test_to_wkt_point_empty() -> None: ...
def test_to_wkt_empty_z(wkt) -> None: ...
def test_to_wkt_geometrycollection_with_point_empty() -> None: ...
def test_to_wkt_multipoint_with_point_empty() -> None: ...
def test_to_wkt_multipoint_with_point_empty_errors() -> None: ...
def test_repr() -> None: ...
def test_repr_max_length() -> None: ...
def test_repr_multipoint_with_point_empty() -> None: ...
def test_repr_point_z_empty() -> None: ...
def test_to_wkb() -> None: ...
def test_to_wkb_hex() -> None: ...
def test_to_wkb_3D() -> None: ...
def test_to_wkb_none() -> None: ...
def test_to_wkb_exceptions() -> None: ...
def test_to_wkb_byte_order() -> None: ...
def test_to_wkb_srid() -> None: ...
def test_to_wkb_flavor() -> None: ...
def test_to_wkb_flavor_srid() -> None: ...
def test_to_wkb_flavor_unsupported_geos() -> None: ...
def test_to_wkb_point_empty_2d(geom, expected) -> None: ...
def test_to_wkb_point_empty_3d(geom, expected) -> None: ...
def test_to_wkb_point_empty_2d_output_dim_3(geom, expected) -> None: ...
def test_from_wkb_point_empty(wkb, expected_type, expected_dim) -> None: ...
def test_to_wkb_point_empty_srid() -> None: ...
def test_pickle(geom) -> None: ...
def test_pickle_with_srid(geom) -> None: ...
def test_from_geojson(geojson, expected) -> None: ...
def test_from_geojson_exceptions() -> None: ...
def test_from_geojson_warn_on_invalid() -> None: ...
def test_from_geojson_ignore_on_invalid() -> None: ...
def test_from_geojson_on_invalid_unsupported_option() -> None: ...
def test_to_geojson(geometry, expected) -> None: ...
def test_to_geojson_indent(indent) -> None: ...
def test_to_geojson_exceptions() -> None: ...
def test_to_geojson_point_empty(geom) -> None: ...
def test_geojson_all_types(geom) -> None: ...
