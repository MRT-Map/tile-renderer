All Functions
=============

Main
----
.. py:function:: render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int[, assetsDir="skins/assets/", verbosityLevel=1, tiles: list])

   Renders tiles from given coordinates and zoom values.

   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see "Renderer input format")
   * dict **nodeList**: a dictionary of nodes (see "Renderer input format")
   * dict **skinJson**: a JSON of the skin used to render tiles
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomRange**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units
   * str **assetsDir** *(default: "skins/assets/")*: the asset directory for the skin
   * int **verbosityLevel** *(default: 1)*: the verbosity level of the output by the function. Use any number from 0 to 2
   * list[tuple] **tiles** *(optional)*: a list of tiles to render, given in tuples of ``(z,x,y)`` where z = zoom and x,y = tile coordinates

   **Returns**

   * **None**

Tools
-----

.. py:function:: renderer.tools.lineToTiles(coords: list, minZoom: int, maxZoom: int, maxZoomRange: int)

   Generates tile coordinates from list of regular coordinates using ``renderer.tools.coordToTiles()``. Mainly for rendering whole PLAs.

   **Parameters**

   * list[tuple] **coords** of coordinates in tuples of ``(x,y)``
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: renderer.tools.coordToTiles(coord: list, minZoom: int, maxZoom: int, maxZoomRange: int)

   Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

   **Parameters**

   * list[int/float] **coord**: Coordinates provided in the form ``[x,y]``
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: renderer.tools.plaJson_calcRenderedIn(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int)
   Like ``renderer.tools.lineToTiles()``, but for a JSON or dictionary of PLAs.

   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see "Renderer input format")
   * dict **nodeList**: a dictionary of nodes (see "Renderer input format")
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: renderer.tools.plaJson_findEnds(plaList: dict, nodeList: dict)

   Finds the minimum and maximum X and Y values of a JSON or dictionary of PLAs.
   
   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see "Renderer input format")
   * dict **nodeList**: a dictionary of nodes (see "Renderer input format")
   
   **Returns**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`
   
.. py:function:: renderer.tools.nodesToCoords(nodes: list, nodeList: dict)
   
   Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.
   
   **Parameters**

   * list **nodes**: a list of node IDs
   * dict **nodeList**: a dictionary of nodes (see "Renderer input format")
   
   **Returns**

   * **list[tuple]** A list of coordinates
   
.. py:function:: renderer.tools.findPlasAttachedToNode(nodeId: str, plaList: dict)

   Finds which PLAs attach to a node.
   
   **Parameters**

   * str **nodeId**: the node to search for
   * dict **plaList**: a dictionary of PLAs (see "Renderer input format")
   
   **Returns**

   * **list[tuple]** A tuple in the form of (plaId, posInNodeList)

Math Tools
----------
.. py:function:: renderer.mathtools.midpoint(x1, y1, x2, y2, o[, returnBoth=False])

   Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points
   * int/float **o**: the offset from the line. If positive, the point above the line is returned; if negative, the point below the line is returned
   * bool **returnBoth** *(default=False)*: if True, it will return both possible points.
   
   **Returns**
   
   * *returnBoth=False* **tuple** A tuple in the form of (x, y, rot)
   * *returnBoth=True* **list[tuple]** A list of two tuples in the form of (x, y, rot)
   
.. py:function:: renderer.mathtools.linesIntersect(x1: Union[int,float], y1: Union[int,float], x2: Union[int,float], y2: Union[int,float], x3: Union[int,float], y3: Union[int,float], x4: Union[int,float], y4: Union[int,float])
   
   Finds if two segments intersect.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points of the first segment.
   * int/float **x3, y3, x4, y4**: the coordinates of two points of the second segment.
   
   **Returns**
   
   * **bool** Whether the two segments intersect.
   
.. py:function:: renderer.mathtools.pointInPoly(xp: Union[int,float], yp: Union[int,float], coords: list)
   
   Finds if a point is in a polygon.
   **WARNING: If your polygon has a lot of corners, this will take very long.**
   
   **Parameters**
   
   * int/float **xp, yp**: the coordinates of the point.
   * list **coords**: the coordinates of the polygon; give in (x,y)
   
   **Returns**
   
   * **bool** Whether the point is inside the polygon.
   
.. py:function:: renderer.mathtools.polyCenter(coords: list)

   Finds the center point of a polygon.
   
   **Parameters**
   
   * list **coords**: the coordinates of the polygon; give in (x,y)
   
   **Returns**
   
   * **tuple** The center of the polygon, given in (x,y)
   
.. py:function:: renderer.mathtools.lineInBox(line: list, top: int, bottom: int, left: int, right: int)
   
   Finds if any nodes of a line go within the box.
   
   **Parameters**
   
   * list **line**: the line to check for
   * int **top, bottom, left, right**: the bounds of the box
   
   **Returns**
   
   * **bool** Whether any nodes of a line go within the box.
   
.. py:function:: renderer.mathtools.dash(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], d: Union[int, float] [, o=0, emptyStart=False])
   
   Finds points along a segment that are a specified distance apart.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points of the segment
   * int/float **d**: the distance between points
   * int/float **o** *(default: 0)*: the offset from (x1,y1) towards (x2,y2) before dashes are calculated
   * bool **emptyStart** *(default: False)*: Whether to start the line from (x1,y1) empty before the start of the next dash
   
   **Returns**
   
   * **list[list[tuple]]** A list of points along the segment, given in [[(x1, y1), (x2, y2)], etc]

.. py:function:: renderer.mathtools.dashOffset(coords: list, d: Union[int, float])

   Calculates the offsets on each coord of a line for a smoother dashing sequence.

   **Parameters**

   * list **coords**: the coords of the line
   * int/float **d**: the distance between points

   **Returns**

   * **list[float]** The offsets of each coordinate

.. py:function:: renderer.mathtools.rotateAroundPivot(x: Union[int, float], y: Union[int, float], px: Union[int, float], py: Union[int, float], theta: Union[int, float])

   Rotates a set of coordinates around a pivot point.

   **Parameters**

   * int/float **x, y**: the coordinates to be rotate
   * int/float **px, py**: the coordinates of the pivot
   * int/float **theta**: how many **degrees** to rotate

   **Returns**

   * **tuple** The rotated coordinates, given in (x,y)

Utilities
---------

.. py:function:: renderer.utils.coordListIntegrity(coords: list[, error=False, silent=False])

Checks integrity of a list of coordinates.

**Parameters**

* list **coords**: a list of coordinates.
* bool **error** *(default=False)*: if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(default=False)*: if True, info messages will not be shown.

**Returns**

* **list[str]** A list of errors

.. py:function:: renderer.utils.tileCoordListIntegrity(tiles: list, minZoom: int, maxZoom: int[, error=False, silent=False])

Checks integrity of a list of tile coordinates.

**Parameters**

* list **tiles**: a list of tile coordinates.
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* bool **error** *(default=False)*: if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(default=False)*: if True, info messages will not be shown.

**Returns**

* **list[str]** A list of errors

.. py:function:: renderer.utils.nodeListIntegrity(nodes: list, nodeList: dict[, error=False, silent=False])

Checks integrity of a list of node IDs.

**Parameters**

* list **nodes**: a list of node IDs.
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(default=False)*: if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(default=False)*: if True, info messages will not be shown.

**Returns**

* **list[str]** A list of errors

.. py:function:: renderer.utils.nodeJsonIntegrity(nodeList: dict[, error=False])

Checks integrity of a dictionary/JSON of nodes.

**Parameters**

* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(default=False)*: if True, when a problem is spotted an error is raised instead of an warning message.

**Returns**

* **list[str]** A list of errors

.. py:function:: renderer.utils.plaJsonIntegrity(plaList: dict, nodeList: dict[, error=False])

Checks integrity of a dictionary/JSON of PLAs.

**Parameters**
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(default=False)*: if True, when a problem is spotted an error is raised instead of an warning message.

**Returns**

* **list[str]** A list of errors