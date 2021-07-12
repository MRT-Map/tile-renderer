All Functions
=============

**Useful information**

* PLA = Points, Lines and Areas
* Type aliases:

  *  RealNum = Union[int, float]
  *  Coord = Tuple[RealNum, RealNum]
  *  TileCoord = Tuple[int, int, int]

Main
----
.. py:currentmodule:: renderer

.. py:function:: render(plaList: dict, nodeList: dict, skinJson: dict, minZoom: int, maxZoom: int, maxZoomRange: RealNum, saveImages: bool=True, saveDir: str="", assetsDir: str=os.path.dirname(__file__)+"/skins/assets/", \
                 processes: int=1, tiles: Optional[List[TileCoord]]=None, offset: Tuple[RealNum, RealNum]=(0,0)) -> Dict[str, Image]

   Renders tiles from given coordinates and zoom values.

   .. warning::
      Run this function under ``if __name__ == "__main__"``, or else there would be a lot of multiprocessing RuntimeErrors.

   :param dict plaList: a dictionary of PLAs (see :ref:`formats`)
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
   :param dict skinJson: a JSON of the skin used to render tiles (see :ref:`formats`)
   :param int minZoom: minimum zoom value
   :param int maxZoom: maximum zoom value
   :param RealNum maxZoomRange: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units
   :param int saveImages: whether to save the tile images in a folder or not
   :param str saveDir: the directory to save tiles in
   :param str assetsDir: the asset directory for the skin
   :param int processes: The amount of processes to run for rendering
   :param Optional[List[TileCoord]] tiles: a list of tiles to render, given in tuples of ``(z,x,y)`` where z = zoom and x,y = tile coordinates
   :param Tuple[RealNum, RealNum] offset: the offset to shift all node coordinates by, given as ``(x,y)``

   :returns: Given in the form of ``"(tile coord)": (PIL Image)``
   :rtype: Dict[str, Image]

   :raises ValueError: if maxZoom < minZoom

.. py:function:: tileMerge(images: Union[str, Dict[str, Image]], saveImages: bool=True, saveDir: str="tiles/", zoom: List[int]=[]) -> List[Image]

   Merges tiles rendered by ``renderer.render()``.

   :param Union[str, Dict[str, Image]] images: Give in the form of ``"(tile coord)": (PIL Image)``, like the return value of ``renderer.render()``, or as a path to a directory.
   :param bool saveImages: whether to save the tile imaegs in a folder or not
   :param str saveDir: the directory to save tiles in
   :param List[int] zoom: if left empty, automatically calculates all zoom values based on tiles; otherwise, the layers of zoom to merge.

   :returns: Given in the form of ``"(Zoom)": (PIL Image)``
   :rtype: List[Image]

Tools
-----
.. py:currentmodule:: renderer.tools.plaJson

.. py:function:: findEnds(plaList: dict, nodeList: dict) -> Tuple[RealNum, RealNum, RealNum, RealNum]

   Finds the minimum and maximum X and Y values of a JSON or dictionary of PLAs.
   
   :param dict plaList: a dictionary of PLAs (see :ref:`formats`)
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
   
   :returns: Returns in the form `(xMax, xMin, yMax, yMin)`
   :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]
   

.. py:function:: renderedIn(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: RealNum) -> List[TileCoord]
   
   Like ``renderer.tools.lineToTiles()``, but for a JSON or dictionary of PLAs.

   :param dict plaList: a dictionary of PLAs (see :ref:`formats`)
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
   :param int minZoom: minimum zoom value
   :param int maxZoom: maximum zoom value
   :param RealNum maxZoomRange: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   :returns: A list of tile coordinates
   :rtype: List[TileCoord]

   :raises ValueError: if maxZoom < minZoom

.. py:function:: toGeoJson(plaList: dict, nodeList: dict, skinJson: dict) -> dict

   Converts PLA Json into GeoJson (with nodes and skin).
   :param dict plaList: a dictionary of PLAs (see :ref:`formats`)
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
   :param dict skinJson: a JSON of the skin (see :ref:`formats`)

   :returns: A GeoJson dictionary
   :rtype: dict

.. py:currentmodule:: renderer.tools.geoJson

.. py:function:: toNodePlaJson(geoJson: dict) -> Tuple[dict, dict]

   Converts GeoJson to PLA and Node JSONs.

   :param dict geoJson: a GeoJson dictionary

   :returns: Given in ``plaJson, nodeJson``
   :rtype: Tuple[dict, dict]

.. py:currentmodule:: renderer.tools.tile

.. py:function:: findEnds(coords: List[TileCoord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]

   Find the minimum and maximum x/y values of a set of tiles coords.

   :param List[TileCoord] coords: a list of tile coordinates, provide in a tuple of (z,x,y)

   :returns: Returns in the form `(xMax, xMin, yMax, yMin)`
   :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]

.. py:currentmodule:: renderer.tools.line

.. py:function:: findEnds(coords: List[Coord]) -> Tuple[RealNum, RealNum, RealNum, RealNum]

   Find the minimum and maximum x/y values of a set of coords.

   :param List[Coord] coords: a list of coordinates, provide in a tuple of (x,y)

   :returns: Returns in the form `(xMax, xMin, yMax, yMin)`
   :rtype: Tuple[RealNum, RealNum, RealNum, RealNum]

.. py:function:: toTiles(coords: List[Coord], minZoom: int, maxZoom: int, maxZoomRange: RealNum) -> List[TileCoord]

   Generates tile coordinates from list of regular coordinates using ``renderer.tools.coordToTiles()``. Mainly for rendering whole PLAs.

   :param List[Coord] coords: of coordinates in tuples of ``(x,y)``
   :param int minZoom: minimum zoom value
   :param int maxZoom: maximum zoom value
   :param RealNum maxZoomRange: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   :returns: A list of tile coordinates
   :rtype: List[TileCoord]

   :raises ValueError: if maxZoom < minZoom
   :raises ValueError: if empty list of coords given

.. py:currentmodule:: renderer.tools.node

.. py:function:: findPlasAttached(nodeId: str, plaList: dict) -> List[Tuple[str, int]]

   Finds which PLAs attach to a node.
   
   :param str nodeId: the node to search for
   :param dict plaList: a dictionary of PLAs (see :ref:`formats`)
   
   :returns: A tuple in the form of ``(plaId, posInNodeList)``
   :rtype: List[Tuple[str, int]]

.. py:function:: toCoords(nodes: List[str], nodeList: dict) -> List[Coord]
   
   Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.
   
   :param list nodes: a list of node IDs
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
   
   :returns: A list of coordinates
   :rtype: List[Coord]

   :raises KeyError: if a node does not exist

.. py:currentmodule:: renderer.tools.coord

.. py:function:: toTiles(coord: Coord, minZoom: int, maxZoom: int, maxZoomRange: RealNum) -> List[TileCoord]

   Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

   :param Coord coord: Coordinates provided in the form ``(x,y)``
   :param int minZoom: minimum zoom value
   :param int maxZoom: maximum zoom value
   :param RealNum maxZoomRange: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a ``maxZoom`` of 5 and a ``maxZoomValue`` of 8 will make a 5-zoom tile cover 8 units

   :returns: A list of tile coordinates
   :rtype: List[TileCoord]

   :raises ValueError: if maxZoom < minZoom

Math Tools
----------
.. py:currentmodule:: renderer.mathtools

.. py:function:: midpoint(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, o: RealNum, n: int=1, returnBoth: bool=False) -> Union[List[Tuple[RealNum, RealNum, RealNum]], List[List[Tuple[RealNum, RealNum, RealNum]]]]

   Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.
      
   :param RealNum x1: the x-coordinate of the 1st point
   :param RealNum y1: the y-coordinate of the 1st point
   :param RealNum x2: the x-coordinate of the 2nd point
   :param RealNum y2: the y-coordinate of the 2nd point
   :param RealNum o: the offset from the line. If positive, the point above the line is returned; if negative, the point below the line is returned
   :param int n: the number of midpoints on a single segment
   :param bool returnBoth: if True, it will return both possible points.
      
   :return: A list of *(lists of, when returnBoth=True)* tuples in the form of (x, y, rot)
   :rtype: List[Tuple[RealNum, RealNum, RealNum]] *when returnBoth=False,* List[List[Tuple[RealNum, RealNum, RealNum]]] *when returnBoth=True*
   
.. py:function:: linesIntersect(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, x3: RealNum, y3: RealNum, x4: RealNum, y4: RealNum) -> bool:
   
   Finds if two segments intersect.
    
   :param RealNum x1: the x-coordinate of the 1st point of the 1st segment.
   :param RealNum y1: the y-coordinate of the 1st point of the 1st segment.
   :param RealNum x2: the x-coordinate of the 2nd point of the 1st segment.
   :param RealNum y2: the y-coordinate of the 2nd point of the 1st segment.
   :param RealNum x3: the x-coordinate of the 1st point of the 2nd segment.
   :param RealNum y3: the y-coordinate of the 1st point of the 2nd segment.
   :param RealNum x4: the x-coordinate of the 2nd point of the 2nd segment.
   :param RealNum y4: the y-coordinate of the 2nd point of the 2nd segment.
      
   :returns: Whether the two segments intersect.
   :rtype: bool
   
.. py:function:: pointInPoly(xp: RealNum, yp: RealNum, coords: List[Coord]) -> bool
   
   Finds if a point is in a polygon.
      
   :param RealNum xp: the x-coordinate of the point.
   :param RealNum yp: the y-coordinate of the point.
   :param list List[Coord]: the coordinates of the polygon; give in (x,y)
      
   :returns: Whether the point is inside the polygon.
   :rtype: bool
   
.. py:function:: polyCenter(coords: List[Coord]) -> Coord

   Finds the center point of a polygon.
      
   :param List[Coord] coords: the coordinates of the polygon; give in ``(x,y)``
      
   :returns: The center of the polygon, given in ``(x,y)``
   :rtype: Coord
   
.. py:function:: lineInBox(line: List[Coord], top: RealNum, bottom: RealNum, left: RealNum, right: RealNum) -> bool
   
   Finds if any nodes of a line go within the box.
      
   :param List[Coord] line: the line to check for
   :param RealNum top: the bounds of the box
   :param RealNum bottom: the bounds of the box
   :param RealNum left: the bounds of the box
   :param RealNum right: the bounds of the box
      
   :returns: Whether any nodes of a line go within the box.
   :rtype: bool
   
.. py:function:: dash(x1: RealNum, y1: RealNum, x2: RealNum, y2: RealNum, d: RealNum, g: RealNum, o: RealNum=0, emptyStart: bool=False) -> List[List[Coord]]
   
   Finds points along a segment that are a specified distance apart.
      
   :param RealNum x1: the x-coordinate of the 1st point
   :param RealNum y1: the y-coordinate of the 1st point
   :param RealNum x2: the x-coordinate of the 2nd point
   :param RealNum y2: the y-coordinate of the 2nd point
   :param RealNum d: the length of a single dash
   :param RealNum g: the length of the gap between dashes
   :param RealNum o: the offset from (x1,y1) towards (x2,y2) before dashes are calculated
   :param bool emptyStart: Whether to start the line from (x1,y1) empty before the start of the next dash
      
   :returns: A list of points along the segment, given in [[(x1, y1), (x2, y2)], etc]
   :rtype: List[List[Coord]]

.. py:function:: dashOffset(coords: List[Coord], d: RealNum, g: RealNum) -> Tuple[RealNum, bool]

   Calculates the offsets on each coord of a line for a smoother dashing sequence.

   :param List[Coord] coords: the coords of the line
   :param RealNum d: the length of a single dash
   :param RealNum g: the length of the gap between dashes

   :returns: The offsets of each coordinate, and whether to start the next segment with emptyStart, given in (offset, emptyStart)
   :rtype: Tuple[RealNum, bool]

.. py:function:: rotateAroundPivot(x: RealNum, y: RealNum, px: RealNum, py: RealNum, theta: RealNum) -> Coord

   Rotates a set of coordinates around a pivot point.

   :param RealNum x: the x-coordinate to be rotated
   :param RealNum y: the y-coordinate to be rotated
   :param RealNum px: the x-coordinate of the pivot
   :param RealNum py: the y-coordinate of the pivot
   :param RealNum theta: how many **degrees** to rotate

   :returns: The rotated coordinates, given in (x,y)
   :rtype: Coord

.. py:function:: pointsAway(x: RealNum, y: RealNum, d: RealNum, m: RealNum) -> List[Coord]

   Finds two points that are a specified distance away from a specified point, all on a straight line.

   :param RealNum x, y: the coordinates of the original point
   :param RealNum d: the distance the two points from the original point
   :param RealNum m: the gradient of the line. Give ``None`` for a gradient of undefined.

   :returns: Given in [(x1, y1), (x2, y2)]
   :rtype: List[Coord]

Validate
--------
.. py:currentmodule:: renderer.validate

.. py:function:: vCoords(coords: List[Coord]) -> True

   Validates a list of coordinates.
      
   :param List[Coord] coords: a list of coordinates.
      
   :returns: Returns True if no errors

.. py:function:: vTileCoords(tiles: List[TileCoord], minZoom: int, maxZoom: int) -> True

   Validates a list of tile coordinates.
      
   :param List[TileCoord] tiles: a list of tile coordinates.
   :param int minZoom: minimum zoom value
   :param int maxZoom: maximum zoom value
      
   :returns: Returns True if no errors

.. py:function:: vNodeList(nodes: List[str], nodeList: dict) -> True

   Validates a list of node IDs.
      
   :param List[str] nodes: a list of node IDs.
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
      
   :returns: Returns True if no errors

.. py:function:: vNodeJson(nodeList: dict) -> True

   Validates a dictionary/JSON of nodes.
      
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
      
   :returns: Returns True if no errors

.. py:function:: vPlaJson(plaList: dict, nodeList: dict) -> True

   Validates a dictionary/JSON of PLAs.
      
   :param dict plaList: a dictionary of PLAs (see :ref:`formats`)
   :param dict nodeList: a dictionary of nodes (see :ref:`formats`)
      
   :returns: Returns True if no errors

.. py:function:: vSkinJson(skinJson: dict) -> True
   
   Validates a skin JSON file.

   :param dict skinJson: the skin JSON file
   
   :returns: Returns True if no errors

.. py:function:: vGeoJson(geoJson: dict) -> True
   
   Validates a GeoJson file.

   :param dict geoJson: the GeoJson file
   
   :returns: Returns True if no errors

Misc
----
.. py:currentmodule:: renderer.misc

.. py:function:: getSkin(name: str) -> dict
   
   Gets a skin from inside the package.

   :param str name: the name of the skin
   
   :returns: The skin JSON
   :rtype: dict

   :raises FileNotFoundError: if skin does not exist