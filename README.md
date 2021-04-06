# tile-renderer
Tile renderer for leaflet.js usage, made by 7d

**Documentation: [https://tile-renderer.readthedocs.io/en/latest/]**

## Current version: v0.7
* **v0.7 (6/4/21)**
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
  * estimated that last beta release before v1.0 is v0.8 or v0.9
* **Past changelogs can be found in [https://tile-renderer.readthedocs.io/en/latest/changelog/]**
