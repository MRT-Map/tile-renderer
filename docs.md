# Tile Renderer Documentation (v0.1)

## Renderer input format
Points, Lines & Areas:
```
{
  "(nameid)": [
    {
      "type": "(type)",
      "shape": "(point/line/area)",
      "displayname": "(displayname)"
      "layer": layer_no,
      "coords": [nodeid, nodeid, ...],
      "renderedin": [(z,x,y), (z,x,y), ...]
      "attrs": {
        "(attr name)": "(attr val)",
        // etc
      }
    },
  ]
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

### `renderer.render(plaList: dict, nodeList: dict, minZoom: int, maxZoom: int, maxZoomRange: int[, tiles=...])`
Renders tiles from given coordinates and zoom values.
**NOTE: INCOMPLETE**

#### Arguments
* dict **plaList**: a dictionary of points, lines and areas (see "Renderer input format")
* dict **nodeList**: a dictionary of nodes (see "Renderer input format")
* int **minZoom**: minimum zoom value
* int **maxZoom**: maximum zoom value
* int **maxZoomValue**: range of coordinates covered by a tile in the maximum zoom (how do I phrase this?) For example, a `maxZoom` of 5 and a `maxZoomValue` of 8 will make a 5-zoom tile cover 8 units
* list **tiles** (optional): a list of tiles to render, given in tuples of `(z,x,y)` where z = zoom and x,y = cotile ordinates

#### Returns

### `renderer.tools.coordToTiles(coord: list, minZoom: int, maxZoom: int, maxZoomRange: int)`
TODO

### `renderer.tools.lineToTiles(coords: list, minZoom: int, maxZoom: int, maxZoomRange: int)`
TODO