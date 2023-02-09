from _typeshed import Incomplete
from shapely import count_coordinates as count_coordinates
from shapely import get_coordinates as get_coordinates
from shapely import set_coordinates as set_coordinates
from shapely import transform as transform

from .common import empty as empty
from .common import empty_line_string_z as empty_line_string_z
from .common import empty_point as empty_point
from .common import empty_point_z as empty_point_z
from .common import geometry_collection as geometry_collection
from .common import geometry_collection_z as geometry_collection_z
from .common import line_string as line_string
from .common import line_string_z as line_string_z
from .common import linear_ring as linear_ring
from .common import multi_line_string as multi_line_string
from .common import multi_point as multi_point
from .common import multi_polygon as multi_polygon
from .common import point as point
from .common import point_z as point_z
from .common import polygon as polygon
from .common import polygon_with_hole as polygon_with_hole
from .common import polygon_z as polygon_z

nested_2: Incomplete
nested_3: Incomplete

def test_count_coords(geoms, count) -> None: ...
def test_get_coords(geoms, x, y, include_z) -> None: ...
def test_get_coords_index(geoms, index) -> None: ...
def test_get_coords_index_multidim(order) -> None: ...
def test_get_coords_3d(geoms, x, y, z, include_z) -> None: ...
def test_set_coords(geoms, count, has_ring, include_z) -> None: ...
def test_set_coords_nan() -> None: ...
def test_set_coords_breaks_ring() -> None: ...
def test_set_coords_0dim() -> None: ...
def test_set_coords_mixed_dimension(include_z) -> None: ...
def test_transform(geoms, include_z): ...
def test_transform_0dim(): ...
def test_transform_check_shape(): ...
def test_transform_correct_coordinate_dimension(): ...
def test_transform_empty_preserve_z(geom): ...
def test_transform_remove_z(geom): ...