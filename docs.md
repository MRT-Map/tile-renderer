# Tile Renderer Documentation (v0.5)

## Useful Information
* To convert tuple to list efficiently use *(tuple)
* PLA = Points, Lines and Areas

## Renderer input format
PLAs:
```
{
  "(nameid)": {
    "type": "(type)",
    "displayname": "(displayname)",
    "description": "(description)"
    "layer": layer_no,
    "nodes": [nodeid, nodeid, False],
    "attrs": {
      "(attr name)": "(attr val)",
    // etc
    }
  },
  //etc
}
```

Nodes (Note: Nodes != Points):
```
{
  "(nodeid)": {
    "x": x,
    "y": y,
    "connections": [
      {
        "nodeid": nodeid,
        "mode": nameid, //lines only
        "cost": cost, //lines only, time will be calculated from distance and speed
      },
      // etc
    ]
  }
}
```

## API - Main

### `renderer.render(plaList, nodeList, skinJson, minZoom, maxZoom, maxZoomRange[, tiles=False])`
Renders tiles from given coordinates and zoom values.
**NOTE: INCOMPLETE**

#### Arguments
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* dict **skinJson**: a JSON of the skin used to render tiles
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a `maxZoom` of 5 and a `maxZoomValue` of 8 will make a 5-zoom tile cover 8 units
* list[tuple] **tiles** *(optional)*: a list of tiles to render, given in tuples of `(z,x,y)` where z = zoom and x,y = tile coordinates

#### Returns
* **None**

## API - Main

### `renderer.tools.lineToTiles(coords, minZoom, maxZoom, maxZoomRange)`
Generates tile coordinates from list of regular coordinates using `renderer.tools.coordToTiles()`. Mainly for rendering whole PLAs.

### Arguments
* list[tuple] **coords** of coordinates in tuples of `(x,y)`
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a `maxZoom` of 5 and a `maxZoomValue` of 8 will make a 5-zoom tile cover 8 units

#### Returns
* **list[tuple]** A list of tile coordinates

## API - Tools

### `renderer.tools.coordToTiles(coord, minZoom, maxZoom, maxZoomRange)`
Returns all tiles in the form of tile coordinates that contain the provided regular coordinate.

#### Arguments
* list[int/float] **coord**: Coordinates provided in the form `[x,y]`
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a `maxZoom` of 5 and a `maxZoomValue` of 8 will make a 5-zoom tile cover 8 units

#### Returns
* **list[tuple]** A list of tile coordinates

### `renderer.tools.plaJson_calcRenderedIn(plaList, nodeList, minZoom, maxZoom, maxZoomRange)`
Like `renderer.tools.lineToTiles()`, but for a JSON or dictionary of PLAs.

### Arguments
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a `maxZoom` of 5 and a `maxZoomValue` of 8 will make a 5-zoom tile cover 8 units

#### Returns
* **list[tuple]** A list of tile coordinates

### `renderer.tools.plaJson_findEnds(plaList, nodeList)`
Finds the minimum and maximum X and Y values of a JSON or dictionary of PLAs.

### Arguments
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")

#### Returns
* **tuple** Returns in the form `(xMax, xMin, yMax, yMin)`

### `renderer.tools.nodesToCoords(nodes, nodeList)`
Converts a list of nodes IDs into a list of coordinates with a node dictionary/JSON as its reference.

#### Arguments
* list **nodes**: a list of node IDs
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")

#### Returns
* **list[tuple]** A list of coordinates

### `renderer.tools.findPlasAttachedToNode(nodeId, plaList)`
Finds which PLAs attach to a node.

#### Arguments
* str **nodeId**: the node to search for
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")

#### Returns
* **list[tuple]** A tuple in the form of (plaId, posInNodeList)

### `renderer.tools.lineInBox(line, top, bottom, left, right)`
Finds if any nodes of a line go within the box.

#### Arguments
* list **line**: the line to check for
* int **top, bottom, left, right**: the bounds of the box

#### Returns
* **bool** Whether any nodes of a line go within the box.

## API - Math Tools

### `renderer.mathtools.midpoint(x1, y1, x2, y2, o[, returnBoth=False])`
Calculates the midpoint of two lines, offsets the distance away from the line, and calculates the rotation of the line.

#### Arguments
* int/float **x1, y1, x2, y2**: the coordinates of two points
* int/float **o**: the offset from the line. If positive, the point above the line is returned; if negative, the point below the line is returned
* bool **returnBoth** *(optional)*: False by default; if True, it will return both possible points.

#### Returns
* *returnBoth=False* **tuple** A tuple in the form of (x, y, rot)
* *returnBoth=True* **list[tuple]** A list of two tuples in the form of (x, y, rot)

### `renderer.mathtools.linesIntersect(x1, y1, x2, y2, x3, y3, x4, y4)`
Finds if two segments intersect.

#### Arguments
* int/float **x1, y1, x2, y2**: the coordinates of two points of the first segment.
* int/float **x3, y3, x4, y4**: the coordinates of two points of the second segment.

#### Returns
* **bool** Whether the two segments intersect.

### `renderer.mathtools.pointInPoly(xp, yp, coords)`
Finds if a point is in a polygon.
**WARNING: If your polygon has a lot of corners, this will take very long.**

#### Arguments
* int/float **xp, yp**: the coordinates of the point.
* list **coords**: the coordinates of the polygon; give in (x,y)

#### Returns
* **bool** Whether the point is inside the polygon.

## API - Utils

### `renderer.utils.coordListIntegrity(coords[, error=False, silent=False])`
Checks integrity of a list of coordinates.

### Arguments
* list **coords**: a list of coordinates.
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(optional)*: False by default; if True, info messages will not be shown.

### Returns
* **list[str]** A list of errors

### `renderer.utils.tileCoordListIntegrity(tiles, minZoom, maxZoom[, error=False, silent=False])`
Checks integrity of a list of tile coordinates.

### Arguments
* list **tiles**: a list of tile coordinates.
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(optional)*: False by default; if True, info messages will not be shown.

### Returns
* **list[str]** A list of errors

### `renderer.utils.nodeListIntegrity(nodes, nodeList[, error=False, silent=False])`
Checks integrity of a list of node IDs.

### Arguments
* list **nodes**: a list of node IDs.
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(optional)*: False by default; if True, info messages will not be shown.

### Returns
* **list[str]** A list of errors

### `renderer.utils.nodeJsonIntegrity(nodeList[, error=False])`
Checks integrity of a dictionary/JSON of nodes.

### Arguments
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.

### Returns
* **list[str]** A list of errors

### `renderer.utils.plaJsonIntegrity(plaList, nodeList[, error=False])`
Checks integrity of a dictionary/JSON of PLAs.

### Arguments
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.

### Returns
* **list[str]** A list of errors