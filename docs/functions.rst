All Functions
=============

**Useful information**

* To convert tuple to list efficiently use *(tuple)
* PLA = Points, Lines and Areas

Main
----
.. py:function:: renderer.render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: int[, verbosityLevel=1, saveImages=True, saveDir="tiles/", assetsDir="skins/assets/", tiles: list])

   Renders tiles from given coordinates and zoom values.

   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   * dict **skinJson**: a JSON of the skin used to render tiles
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomRange**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units
   * int **verbosityLevel** *(default: 1)*: the verbosity level of the output by the function. Use any number from 0 to 2
   * int **saveImages** *(default: True)*: whether to save the tile images in a folder or not
   * str **saveDir** *(default: "")*: the directory to save tiles in
   * str **assetsDir** *(default: "renderer/skins/assets/")*: the asset directory for the skin
   * list[tuple] **tiles** *(default: None)*: a list of tiles to render, given in tuples of ``(z,x,y)`` where z = zoom and x,y = tile coordinates

   **Returns**

   * **dict** Given in the form of ``"(tile coord)": (PIL Image)``

.. py:function:: tileMerge(images: Union[str, dict] [, verbosityLevel=1, saveImages=True, saveDir="tiles/", zoom=[]])

   Merges tiles rendered by ``renderer.render()``.

   **Parameters**

   * dict **images** Give in the form of ``"(tile coord)": (PIL Image)``, like the return value of ``renderer.render()``
   * int **verbosityLevel** *(default: 1)*: the verbosity level of the output by the function. Use any number from 0 to 2
   * int **saveImages** *(default: True)*: whether to save the tile imaegs in a folder or not
   * str **saveDir** *(default: "")*: the directory to save tiles in
   * list **zoom** *(default: [])*: if left empty, automatically calculates all zoom values based on tiles; otherwise, the layers of zoom to merge.

   **Returns**

   * **dict** Given in the form of ``"(Zoom)": (PIL Image)``

Tools
-----
.. py:function:: renderer.tools.plaJson.toTiles(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int)

   Finds all the tiles that all the PLAs in the JSON will be rendered in.
   
   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units
   
   **Returns**

   * **list[tuples]** A list of tile coordintes

.. py:function:: renderer.tools.plaJson.findEnds(plaList: dict, nodeList: dict)

   Finds the minimum and maximum X and Y values of a JSON or dictionary of PLAs.
   
   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`
   

.. py:function:: renderer.tools.plaJson.renderedIn(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int)
   
   Like ``renderer.tools.lineToTiles()``, but for a JSON or dictionary of PLAs.

   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: renderer.tools.tile.findEnds(coords: list)

   Find the minimum and maximum x/y values of a set of tiles coords.

   **Parameters**

   * list **coords**: a list of tile coordinates, provide in a tuple of (z,x,y)

   **Return**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`

.. py:function:: renderer.tools.line.findEnds(coords: list)

   Find the minimum and maximum x/y values of a set of coords.

   **Parameters**

   * list **coords**: a list of coordinates, provide in a tuple of (x,y)

   **Return**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`

.. py:function:: renderer.tools.line.toTiles(coords: list, minZoom: int, maxZoom: int, maxZoomRange: int)

   Generates tile coordinates from list of regular coordinates using ``renderer.tools.coordToTiles()``. Mainly for rendering whole PLAs.

   **Parameters**

   * list[tuple] **coords** of coordinates in tuples of ``(x,y)``
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: renderer.tools.nodes.findPlasAttached(nodeId: str, plaList: dict)

   Finds which PLAs attach to a node.
   
   **Parameters**

   * str **nodeId**: the node to search for
   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   
   **Returns**

   * **list[tuple]** A tuple in the form of (plaId, posInNodeList)

.. py:function:: renderer.tools.nodes.toCoords(nodes: list, nodeList: dict)
   
   Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.
   
   **Parameters**

   * list **nodes**: a list of node IDs
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**

   * **list[tuple]** A list of coordinates

.. py:function:: renderer.tools.coord.toTiles(coord: list, minZoom: int, maxZoom: int, maxZoomRange: int)

   Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

   **Parameters**

   * list[int/float] **coord**: Coordinates provided in the form ``[x,y]``
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

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
   
.. py:function:: renderer.mathtools.lineInBox(line: list, top: Union[int, float], bottom: Union[int, float], left: Union[int, float], right: Union[int, float])
   
   Finds if any nodes of a line go within the box.
   
   **Parameters**
   
   * list **line**: the line to check for
   * int/float **top, bottom, left, right**: the bounds of the box
   
   **Returns**
   
   * **bool** Whether any nodes of a line go within the box.
   
.. py:function:: renderer.mathtools.dash(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float], d: Union[int, float], g: Union[int, float] [, o=0, emptyStart=False])
   
   Finds points along a segment that are a specified distance apart.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points of the segment
   * int/float **d**: the length of a single dash
   * int/float **g**: the length of the gap between dashes
   * int/float **o** *(default=0)*: the offset from (x1,y1) towards (x2,y2) before dashes are calculated
   * bool **emptyStart** *(default=False)*: Whether to start the line from (x1,y1) empty before the start of the next dash
   
   **Returns**
   
   * **list[list[tuple]]** A list of points along the segment, given in [[(x1, y1), (x2, y2)], etc]

.. py:function:: renderer.mathtools.dashOffset(coords: list, d: Union[int, float], g: Union[int, float])

   Calculates the offsets on each coord of a line for a smoother dashing sequence.

   **Parameters**

   * list **coords**: the coords of the line
   * int/float **d**: the length of a single dash
   * int/float **g**: the length of the gap between dashes

   **Returns**

   * **list[tuple]** The offsets of each coordinate, and whether to start the next segment with emptyStart, given in (offset, emptyStart)

.. py:function:: renderer.mathtools.rotateAroundPivot(x: Union[int, float], y: Union[int, float], px: Union[int, float], py: Union[int, float], theta: Union[int, float])

   Rotates a set of coordinates around a pivot point.

   **Parameters**

   * int/float **x, y**: the coordinates to be rotated
   * int/float **px, py**: the coordinates of the pivot
   * int/float **theta**: how many **degrees** to rotate

   **Returns**

   * **tuple** The rotated coordinates, given in (x,y)

.. py:function:: renderer.mathtools.pointsAway(x: Union[int, float], y: Union[int, float], d: Union[int, float], m: Union[int, float])

   Finds two points that are a specified distance away from a specified point, all on a straight line.

   **Parameters**
   * int/float **x, y**: the coordinates of the original point
   * int/float **d**: the distance the two points from the original point
   * int/float **m**: the gradient of the line. Give ``None`` for a gradient of undefined.

   **Returns**
   * **list[tuple]** Given in [(x1, y1), (x2, y2)]

Validate
--------

.. py:function:: renderer.validate.coords(coords: list)

   Validates a list of coordinates.
   
   **Parameters**
   
   * list **coords**: a list of coordinates.
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: renderer.validate.tileCoords(tiles: list, minZoom: int, maxZoom: int)

   Validates a list of tile coordinates.
   
   **Parameters**
   
   * list **tiles**: a list of tile coordinates.
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: renderer.validate.nodeList(nodes: list, nodeList: dict)

   Validates a list of node IDs.
   
   **Parameters**
   
   * list **nodes**: a list of node IDs.
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: renderer.validate.nodeJson(nodeList: dict)

   Validates a dictionary/JSON of nodes.
   
   **Parameters**
   
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: renderer.validate.plaJson(plaList: dict, nodeList: dict)

   Validates a dictionary/JSON of PLAs.
   
   **Parameters**
   
   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: renderer.validate.skinJson(skinJson: dict)
   
   Validates a skin JSON file.

   **Parameters**

   * dict **skinJson**: the skin JSON file

   **Returns**
   
   * **bool** Returns True if no errors

Misc
----

.. py:function:: renderer.misc.getSkin(sname: str)
   
   Gets a skin from inside the package.

   **Parameters**

   * str **name**: the name of the skin

   **Returns**
   
   * **dict** The skin JSON