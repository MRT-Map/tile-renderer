# tile-renderer
Tile renderer for leaflet.js usage, made by i____7d

## Current version: v0.0
* v0.0
  * started project
  * documented JSON dictionary structure

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
