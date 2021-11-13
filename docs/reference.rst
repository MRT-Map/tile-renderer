Reference
=========
.. py:currentmodule:: renderer

.. py:attribute:: renderer.__version__
    :type: str

    The version.

Main
----
.. autofunction:: render

.. autofunction:: merge_tiles

Tools
-----
.. automodule:: renderer.tools.component_json
   :members:

.. automodule:: renderer.tools.coord
   :members:

.. automodule:: renderer.tools.geo_json
   :members:

.. automodule:: renderer.tools.line
   :members:

.. automodule:: renderer.tools.nodes
   :members:

.. automodule:: renderer.tools.tile
   :members:

Math Tools
----------
.. automodule:: renderer.mathtools
   :members:

Validate
--------
.. automodule:: renderer.validate
   :members:

Types
-----
.. py:attribute:: renderer.types.RealNum
   :type: TypeAlias
   :value: Union[int, float]

   Represents a real number, either an integer or float.

.. py:attribute:: renderer.types.Coord
   :type: TypeAlias
   :value: Tuple[RealNum, RealNum]

   Represents a coordinate in the form ``(x, y)``.

.. py:attribute:: renderer.types.TileCoord
   :type: TypeAlias
   :value: Tuple[int, int, int]

   Represents a tile coordinate in the form ``(z, x, y)``.

.. py:attribute:: renderer.types.Node
   :type: dict

   Represents a node object.

.. py:attribute:: renderer.types.NodeJson
   :type: TypeAlias
   :value: Dict[str, Node]

   Represents a node JSON.

.. py:attribute:: renderer.types.Component
   :type: dict

   Represents a component object.

.. py:attribute:: renderer.types.ComponentJson
   :type: TypeAlias
   :value: Dict[str, Node]

   Represents a component JSON.

.. py:attribute:: renderer.types.SkinInfo
   :type: dict

   Represents the ``info`` portion of a skin JSON.

.. py:attribute:: renderer.types.SkinType
   :type: dict

   Represents a component type in the ``types`` portion of a skin JSON.

.. py:attribute:: renderer.types.SkinJson
   :type: dict

   Represents a skin JSON.

Misc
----

.. automodule:: renderer.misc
   :members: