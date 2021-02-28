# Tile Renderer Documentation (v0.4.1)

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
    "nodes": [nodeid, nodeid, ...],
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

## API

### `renderer.render(plaList, nodeList, skinJson, minZoom, maxZoom, maxZoomRange[, tiles=...])`
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
?

### `renderer.tools.lineToTiles(coords, minZoom, maxZoom, maxZoomRange)`
Generates tile coordinates from list of regular coordinates using `renderer.tools.coordToTiles()`. Mainly for rendering whole PLAs.

### Arguments
* list[tuple] **coords** of coordinates in tuples of `(x,y)`
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a `maxZoom` of 5 and a `maxZoomValue` of 8 will make a 5-zoom tile cover 8 units

#### Returns
* **list[tuple]** A list of tile coordinates

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

### Arguments
* list **nodes**: a list of node IDs.
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")

### Returns
* **list[tuple]** A list of coordinates

### `renderer.utils.coordListIntegrity(coords[, error=..., silent=...])`
Checks integrity of a list of coordinates.

### Arguments
* list **coords**: a list of coordinates.
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(optional)*: False by default; if True, info messages will not be shown.

### Returns
* **list[str]** A list of errors

### `renderer.utils.tileCoordListIntegrity(tiles, minZoom, maxZoom[, error=..., silent=...])`
Checks integrity of a list of tile coordinates.

### Arguments
* list **tiles**: a list of tile coordinates.
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(optional)*: False by default; if True, info messages will not be shown.

### Returns
* **list[str]** A list of errors

### `renderer.utils.nodeListIntegrity(nodes, nodeList[, error=..., silent=...])`
Checks integrity of a list of node IDs.

### Arguments
* list **nodes**: a list of node IDs.
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.
* bool **silent** *(optional)*: False by default; if True, info messages will not be shown.

### Returns
* **list[str]** A list of errors

### `renderer.utils.nodeJsonIntegrity(nodeList[, error=...])`
Checks integrity of a dictionary/JSON of nodes.

### Arguments
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.

### Returns
* **list[str]** A list of errors

### `renderer.utils.plaJsonIntegrity(plaList, nodeList[, error=...])`
Checks integrity of a dictionary/JSON of PLAs.

### Arguments
* dict **plaList**: a dictionary of PLAs (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* bool **error** *(optional)*: False by default; if True, when a problem is spotted an error is raised instead of an warning message.

### Returns
* **list[str]** A list of errors