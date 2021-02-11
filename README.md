# tile-renderer
Tile renderer for leaflet.js usage, made by i____7d

## Current version: v0.0.1 
* v0.0.1 (11/2/21)
  * just a quickie
  * updated input format and added json reading code for test.py
  * added minzoom, maxzoom, maxzoomrange for `renderer.render()`
* **v0.0 (8/2/21)**
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
