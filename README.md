# tile-renderer
Tile renderer for leaflet.js usage, made by i____7d

## Current version: v0.2
* **v0.2 (15/2/21)**
  * Added functions:
    * `renderer.utils.coordListIntegrity()`
    * `renderer.utils.tileCoordListIntegrity()`
    * `renderer.utils.nodeJsonIntegrity()`
    * `renderer.utils.plaJsonIntegrity()`
    * `renderer.utils.nodeListIntegrity()`
    * `renderer.internal.tupleToStr()`
    * `renderer.internal.strToTuple()`
    * `renderer.internal.readJson()`
    * `renderer.internal.writeJson()`
    * `renderer.tools.nodesToCoords()`
    * `renderer.tools.plaJson_findEnds()`
    * `renderer.tools,plaJson_calcRenderedIn()`
  * added more to `renderer.render()`: sorts PLA into tiles now
* **v0.1 (13/2/21)**
  * two new functions: `renderer.tools.coordToTiles()` and `renderer.tools.lineToTiles()`
  * moved renderer input format documentation to docs page
* v0.0.1 (11/2/21)
  * just a quickie
  * updated input format and added json reading code for test.py
  * added minzoom, maxzoom, maxzoomrange for `renderer.render()`
* **v0.0 (8/2/21)**
  * started project
  * documented JSON dictionary structure

## [Documentation](../main/docs.md)