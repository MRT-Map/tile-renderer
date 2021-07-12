All Functions
=============

**Useful information**

* PLA = Points, Lines and Areas
* Type aliases:

  * RealNum = Union[int, float]
  * Coord = Tuple[RealNum, RealNum]
  * TileCoord = Tuple[int, int, int]

Main
----
.. py:currentmodule:: renderer

.. py:function:: render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: RealNum, saveImages: bool=True, saveDir: str="", assetsDir: str=os.path.dirname(__file__)+"/skins/assets/", \
                 processes: int=1, tiles: Optional[List[TileCoord]]=None, offset: Tuple[RealNum, RealNum]=(0,0)) -> Dict[str, Image]

   Renders tiles from given coordinates and zoom values.

   .. warning::
      Run this function under ``if __name__ == "__main__"``, or else there would be a lot of multiprocessing RuntimeErrors.

   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   * dict **skinJson**: a JSON of the skin used to render tiles (see :ref:`formats`)
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomRange**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units
   * int **saveImages** *(default: True)*: whether to save the tile images in a folder or not
   * str **saveDir** *(default: "")*: the directory to save tiles in
   * str **assetsDir** *(default: "renderer/skins/assets/")*: the asset directory for the skin
   * int **processes** The amount of processes to run for rendering
   * list[tuple] **tiles** *(default: None)*: a list of tiles to render, given in tuples of ``(z,x,y)`` where z = zoom and x,y = tile coordinates
   * tuple[int/float] **offset** *(default: (0, 0))*: the offset to shift all node coordinates by, given as ``(x,y)``

   **Returns**

   * **dict** Given in the form of ``"(tile coord)": (PIL Image)``

.. py:function:: tileMerge(images: Union[str, Dict[str, Image]], saveImages: bool=True, saveDir: str="tiles/", zoom: List[int]=[]) -> List[Image]

   Merges tiles rendered by ``renderer.render()``.

   **Parameters**

   * dict **images** Give in the form of ``"(tile coord)": (PIL Image)``, like the return value of ``renderer.render()``
   * int **saveImages** *(default: True)*: whether to save the tile imaegs in a folder or not
   * str **saveDir** *(default: "")*: the directory to save tiles in
   * list **zoom** *(default: [])*: if left empty, automatically calculates all zoom values based on tiles; otherwise, the layers of zoom to merge.

   **Returns**

   * **dict** Given in the form of ``"(Zoom)": (PIL Image)``

Tools
-----
.. py:currentmodule:: renderer.tools

.. py:function:: plaJson.findEnds(plaList: dict, nodeList: dict) -> Tuple[RealNum, RealNum, RealNum, RealNum]

   Finds the minimum and maximum X and Y values of a JSON or dictionary of PLAs.
   
   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`
   

.. py:function:: plaJson.renderedIn(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int) -> List[TileCoord]
   
   Like ``renderer.tools.lineToTiles()``, but for a JSON or dictionary of PLAs.

   **Parameters**

   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: plaJson.toGeoJson(plaList: dict, nodeList: dict, skinJson: dict) -> dict

   Converts PLA Json into GeoJson (with nodes and skin).

   **Parameters**
   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   * dict **skinJson**: a JSON of the skin (see :ref:`formats`)

   **Returns**

   * **dict** A GeoJson dictionary

.. py:function:: geoJson.toNodePlaJson(geoJson: dict) -> Tuple[dict, dict]

   Converts GeoJson to PLA and Node JSONs.

   **Parameters**

   * dict **geoJson** a GeoJson dictionary

   **Returns**
   * **tuple[dict]** Given in ``plaJson, nodeJson``

.. py:function:: tile.findEnds(coords: List[TileCoord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]

   Find the minimum and maximum x/y values of a set of tiles coords.

   **Parameters**

   * list **coords**: a list of tile coordinates, provide in a tuple of (z,x,y)

   **Return**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`

.. py:function:: line.findEnds(coords: List[Coord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]

   Find the minimum and maximum x/y values of a set of coords.

   **Parameters**

   * list **coords**: a list of coordinates, provide in a tuple of (x,y)

   **Return**

   * **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`

.. py:function:: line.toTiles(coords: List[Coord], minZoom: int, maxZoom: int, maxZoomRange: RealNum) -> TileCoord

   Generates tile coordinates from list of regular coordinates using ``renderer.tools.coordToTiles()``. Mainly for rendering whole PLAs.

   **Parameters**

   * list[tuple] **coords** of coordinates in tuples of ``(x,y)``
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   * int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   **Returns**

   * **list[tuple]** A list of tile coordinates

.. py:function:: nodes.findPlasAttached(nodeId: str, plaList: dict) -> List[Tuple[str, int]]

   Finds which PLAs attach to a node.
   
   **Parameters**

   * str **nodeId**: the node to search for
   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   
   **Returns**

   * **list[tuple]** A tuple in the form of (plaId, posInNodeList)

.. py:function:: nodes.toCoords(nodes: List[str], nodeList: dict) -> List[Coord]
   
   Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.
   
   **Parameters**

   * list **nodes**: a list of node IDs
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**

   * **list[tuple]** A list of coordinates

.. py:function:: coord.toTiles(coord: Coord, minZoom: int, maxZoom: int, maxZoomRange: RealNum) -> List[TileCoord]

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
.. py:currentmodule:: renderer.mathtools

.. py:function:: midpoint(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, o: RealNum, n: int=1, returnBoth: bool=False) -> List[Tuple[RealNum, RealNum, RealNum]]

   Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points
   * int/float **o**: the offset from the line. If positive, the point above the line is returned; if negative, the point below the line is returned
   * int/float **n** *(default=1)*: the number of midpoints on a single segment
   * bool **returnBoth** *(default=False)*: if True, it will return both possible points.
   
   **Returns**
   
   * *returnBoth=False* **tuple** A list of tuples in the form of (x, y, rot)
   * *returnBoth=True* **list[tuple]** A list of lists of two tuples in the form of (x, y, rot)
   
.. py:function:: linesIntersect(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, x3: RealNum, y3: RealNum, x4: RealNum, y4: RealNum) -> bool:
   
   Finds if two segments intersect.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points of the first segment.
   * int/float **x3, y3, x4, y4**: the coordinates of two points of the second segment.
   
   **Returns**
   
   * **bool** Whether the two segments intersect.
   
.. py:function:: pointInPoly(xp: RealNum, yp: RealNum, coords: List[Coord]) -> bool
   
   Finds if a point is in a polygon.
   
   **Parameters**
   
   * int/float **xp, yp**: the coordinates of the point.
   * list **coords**: the coordinates of the polygon; give in (x,y)
   
   **Returns**
   
   * **bool** Whether the point is inside the polygon.
   
.. py:function:: polyCenter(coords: List[Coord]) -> Coord

   Finds the center point of a polygon.
   
   **Parameters**
   
   * list **coords**: the coordinates of the polygon; give in (x,y)
   
   **Returns**
   
   * **tuple** The center of the polygon, given in (x,y)
   
.. py:function:: lineInBox(line: List[Coord], top: RealNum, bottom: RealNum, left: RealNum, right: RealNum) -> bool
   
   Finds if any nodes of a line go within the box.
   
   **Parameters**
   
   * list **line**: the line to check for
   * int/float **top, bottom, left, right**: the bounds of the box
   
   **Returns**
   
   * **bool** Whether any nodes of a line go within the box.
   
.. py:function:: dash(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, d: RealNum, g: RealNum, o: RealNum=0, emptyStart: bool=False) -> List[List[Coord]]
   
   Finds points along a segment that are a specified distance apart.
   
   **Parameters**
   
   * int/float **x1, y1, x2, y2**: the coordinates of two points of the segment
   * int/float **d**: the length of a single dash
   * int/float **g**: the length of the gap between dashes
   * int/float **o** *(default=0)*: the offset from (x1,y1) towards (x2,y2) before dashes are calculated
   * bool **emptyStart** *(default=False)*: Whether to start the line from (x1,y1) empty before the start of the next dash
   
   **Returns**
   
   * **list[list[tuple]]** A list of points along the segment, given in [[(x1, y1), (x2, y2)], etc]

.. py:function:: dashOffset(coords: List[Coord], d: RealNum, g: RealNum) -> Tuple[RealNum, bool]

   Calculates the offsets on each coord of a line for a smoother dashing sequence.

   **Parameters**

   * list **coords**: the coords of the line
   * int/float **d**: the length of a single dash
   * int/float **g**: the length of the gap between dashes

   **Returns**

   * **list[tuple]** The offsets of each coordinate, and whether to start the next segment with emptyStart, given in (offset, emptyStart)

.. py:function:: rotateAroundPivot(x: RealNum, y: RealNum, px: RealNum, py: RealNum, theta: RealNum) -> Coord

   Rotates a set of coordinates around a pivot point.

   **Parameters**

   * int/float **x, y**: the coordinates to be rotated
   * int/float **px, py**: the coordinates of the pivot
   * int/float **theta**: how many **degrees** to rotate

   **Returns**

   * **tuple** The rotated coordinates, given in (x,y)

.. py:function:: pointsAway(x: RealNum, y: RealNum, d: RealNum, m: RealNum) -> List[Coord]

   Finds two points that are a specified distance away from a specified point, all on a straight line.

   **Parameters**
   * int/float **x, y**: the coordinates of the original point
   * int/float **d**: the distance the two points from the original point
   * int/float **m**: the gradient of the line. Give ``None`` for a gradient of undefined.

   **Returns**
   * **list[tuple]** Given in [(x1, y1), (x2, y2)]

Validate
--------
.. py:currentmodule:: renderer.validate

.. py:function:: vCoords(coords: List[Coord]) -> True

   Validates a list of coordinates.
   
   **Parameters**
   
   * list **coords**: a list of coordinates.
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: vTileCoords(tiles: List[TileCoord], minZoom: int, maxZoom: int) -> True

   Validates a list of tile coordinates.
   
   **Parameters**
   
   * list **tiles**: a list of tile coordinates.
   * int **minZoom**: minimum zoom value
   * int **maxZoom**: maximum zoom value
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: vNodeList(nodes: List[str], nodeList: dict) -> True

   Validates a list of node IDs.
   
   **Parameters**
   
   * list **nodes**: a list of node IDs.
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: vNodeJson(nodeList: dict) -> True

   Validates a dictionary/JSON of nodes.
   
   **Parameters**
   
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: vPlaJson(plaList: dict, nodeList: dict) -> True

   Validates a dictionary/JSON of PLAs.
   
   **Parameters**
   
   * dict **plaList**: a dictionary of PLAs (see :ref:`formats`)
   * dict **nodeList**: a dictionary of nodes (see :ref:`formats`)
   
   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: vSkinJson(skinJson: dict) -> True
   
   Validates a skin JSON file.

   **Parameters**

   * dict **skinJson**: the skin JSON file

   **Returns**
   
   * **bool** Returns True if no errors

.. py:function:: vGeoJson(geoJson: dict) -> True
   
   Validates a GeoJson file.

   **Parameters**

   * dict **geoJson**: the GeoJson file

   **Returns**
   
   * **bool** Returns True if no errors

Misc
----
.. py:currentmodule:: renderer.misc

.. py:function:: getSkin(name: str) -> dict
   
   Gets a skin from inside the package.

   **Parameters**

   * str **name**: the name of the skin

   **Returns**
   
   * **dict** The skin JSON