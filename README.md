# tile-renderer
Tile renderer for leaflet.js usage, made by i____7d

## Current version: v0.b7
* **v0.7 ()**
  * new `nodeJsonBuilder.py`, intended for use as an assistance for marking nodes on Minecraft
  * fixed `renderer.tools.lineToTiles()`
  * processing and rendering now show ETA
  * fixed oneway roads showing too many arrows
  * added support for lines with unrounded ends through `unroundedEnds` tag
  * updated `renderer.mathtools.dash()` to support offset
  * added `renderer.mathtools.dashOffset()`
  * fixed dashed roads
  * bounding boxes on texts so they don't overlap
  * new logging function (`renderer.internal.log()`)
    * `renderer.render()` has new `verbosityLevel` optional argument, defaults to 1
* **v0.6 (11/3/21)**
  * added loads of PLAs to the default skin; there are now about 90 different PLA types :))
  * tweaked `renderer.mathtools.midpoint()` a bit
  * new functions: `renderer.mathtools.polyCenter()`, `renderer.mathtools.dash()`
  * Moved `renderer.tools.lineInBox()` to `renderer.mathtools.lineInBox()`
  * fixed layers
  * image size is now customisable
    * default skin tile size is now 2048 from 1024
  * added one-way roads
  * added dashed roads, but they're a bit broken right now
  * multiple texts can now be shown on a single line/border
  * improved area centertext; it should now render in the correct center
  * *screams in agony again*
* **v0.5 (28/2/21)**
  * "shape" key in PLA structure removed
  * A Roads, B Roads, local main roads, and simplePoint added to default skin
  * New font for renders (Clear Sans), will be customisable later on
  * Added functions `renderer.mathtools.midpoint()`, `renderer.mathtools.linesIntersect()`, `renderer.mathtools.pointInPoly()`, `renderer.tools.lineInBox()`, `renderer.tools.lineInBox()`, `findPlasAttachedToNode()`
  * Not every info printout is green now; some are white or gray
  * `renderer.render()` now able to render:
    * points
    * text on lines
    * text on borders of areas
    * text in center of areas
    * joined roads
  * ahhh
* v0.4.1 (24/2/21)
  * renderer creates new "tiles" directory to store tiles if directory not present
* **v0.4 (24/2/21)**
  * PLA processing: grouping now only works for lines with "road" tag
  * `renderer.render()` now able to render lines and areas
  * New default skin; simpleLine and simpleArea PLA types added
* **v0.3 (23/2/21)**
  * PLA processing for `renderer.render()`
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