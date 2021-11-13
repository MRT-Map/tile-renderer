Changelog
=========

* v1.3.1 (13/7/21)

  * Super small bugfixes that you probably won't notice
  * Added type hints to all functions
  * Redid the documentation
  * The renderer CLI can now be accessed as just ``renderer`` instead of ``python -m renderer``

* **v1.3 (26/6/21)**

  * New subcommands in CLI:
  
    * ``validate`` and ``vdir``, to validate JSON files
    * ``merge`` to merge 
    * ``plabuilder`` for the new PLA builder
    
  * Area centertext will now break up into multiple lines
  * New PLA builder

    * additionally, builders now have their own submodule
  
* **v1.2 (8/5/21)**

  * ``renderer.render()`` now ignores PLAs if their type is not specified in the skin Json
  * Hollows are now supported in areas
  * New function, ``renderer.validate.v_geo_json()``

    * ``renderer.validate.v_coords()`` now supports lists along with tuples

  * The renderer now has a CLI, to show the help page do ``python -m renderer -h``
  * ``renderer.render()`` now supports float maxZoomRanges
  * New functions: ``renderer.tools.plaJson.to_geo_json()`` and ``renderer.tools.geoJson.to_component_node_json()``

    * these are for translating our custom format of storing geographical format to geoJson
    * (btw why we're not using geoJson is because its harder to store nodes)

  * internal-use files have been moved to ``renderer/internals/``
  * removed ``renderer.tools.plaJson.to_tiles()`` as it's a duplicate of ``renderer.tools.plaJson.rendered_in()``
  * ``renderer.tools.coord.to_tiles()`` now supports tuples as ``coords`` parameter

* **v1.1 (2/5/21)**

  * Added log prefixes to ``renderer.render()`` and ``renderer.tile_merge()``
  * Improved curved line drawing
  * ``renderer.py`` is now split into a package

    * ``renderer.utils`` renamed to ``renderer.validate``
    * all functions of ``renderer.tools`` and ``renderer.validate`` renamed
    * method descriptions added to all functions except those in ``renderer.internal``

  * New function: ``renderer.misc.get_skin()``
  * New logging system that does not clog your terminal
  * changed colour library from ``colorama`` to ``blessed``
  * fixed ``renderer.mergeTiles()``, especially in determining which zooms to merge and retrieving images
  * fixed ``renderer.misc.get_skin()``

* **v1.0 (13/4/21)**

  * added stripes for areas
  * added offset for image centertext
  * new function: ``renderer.tools.line_findEnds()``
  * new function: ``renderer.mathtools.pointsAway()``

    * replaces the messy and unresponsive find-two-points-n-units-away-from-a-point-on-a-straight-line calculations of sympy using trigo
    * rendering should be faster now (``renderer.render.midpoint()``'s speed is now 0-1% of the original speed)
    * **REJECT SYMPY, EMBRACE TRIGONOMETRY, ALL HAIL TRIGO**

  * added a few more level 2 logs to ``renderer.render()``
  * new function: ``renderer.tile_merge()``, used to merge tiles
  * changed output of ``renderer.render()`` from list to dict
  * in counting of rendering operations in ``renderer.render()``, added 1 to each tilePlas to account for text
  * rewrote ``renderer.mathtools.dash()`` and ``renderer.mathtools.dash_offset()``, they're no longer broken :D
  * we've gone out of v0 versions woo

* **v0.8 (7/4/21)**

  * Text of points are now rendered together with texts of lines and areas
  * reordered rendering of PLAs (excluding road tag & text) into functions from if statements
  * got rid of most ``**kwargs``
  * redid integrity checking, mostly with Schema
  * new function: ``renderer.utils.skinJsonIntegrity()``
  * background of tile can now be customised by skin file
  * added offset to area centertext
  * added centerimage to areas

* **v0.7 (6/4/21)**

  * new ``nodeJsonBuilder.py``, intended for use as an assistance for marking nodes on Minecraft
  * fixed ``renderer.tools.lineToTiles()``
  * processing and rendering now show ETA
  * fixed oneway roads showing too many arrows
  * added support for lines with unrounded ends through ``unroundedEnds`` tag
  * updated ``renderer.mathtools.dash()`` to support offset
  * added ``renderer.mathtools.dash_offset()``
  * fixed dashed roads
  * bounding boxes on texts so they don't overlap
  * new logging function (``renderer.internal.log()``)

    * ``renderer.render()`` has new ``verbosityLevel`` optional argument, defaults to 1

  * estimated that last beta release before v1.0 is v0.8 or v0.9

* **v0.6 (11/3/21)**

  * added loads of PLAs to the default skin; there are now about 90 different PLA types :))
  * tweaked ``renderer.mathtools.midpoint()`` a bit
  * new functions: ``renderer.mathtools.poly_center()``, ``renderer.mathtools.dash()``
  * Moved ``renderer.tools.line_in_box()`` to ``renderer.mathtools.line_in_box()``
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
  * Added functions ``renderer.mathtools.midpoint()``, ``renderer.mathtools.lines_intersect()``, ``renderer.mathtools.point_in_poly()``, ``renderer.tools.line_in_box()``, ``renderer.tools.line_in_box()``, ``findPlasAttachedToNode()``
  * Not every info printout is green now; some are white or gray
  * ``renderer.render()`` now able to render:

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
  * ``renderer.render()`` now able to render lines and areas
  * New default skin; simpleLine and simpleArea PLA types added

* **v0.3 (23/2/21)**

  * PLA processing for ``renderer.render()``

* **v0.2 (15/2/21)**

  * Added functions:

    * ``renderer.utils.coordListIntegrity()``
    * ``renderer.utils.tileCoordListIntegrity()``
    * ``renderer.utils.nodeJsonIntegrity()``
    * ``renderer.utils.plaJsonIntegrity()``
    * ``renderer.utils.nodeListIntegrity()``
    * ``renderer.internal._tuple_to_str()``
    * ``renderer.internal._str_to_tuple()``
    * ``renderer.internal._read_json()``
    * ``renderer.internal._write_json()``
    * ``renderer.tools.nodesToCoords()``
    * ``renderer.tools.plaJson_findEnds()``
    * ``renderer.tools,plaJson_calcRenderedIn()``

  * added more to ``renderer.render()``: sorts PLA into tiles now

* **v0.1 (13/2/21)**

  * two new functions: ``renderer.tools.coordToTiles()`` and ``renderer.tools.lineToTiles()``
  * moved renderer input format documentation to docs page

* v0.0.1 (11/2/21)

  * just a quickie
  * updated input format and added json reading code for test.py
  * added minzoom, maxzoom, maxzoomrange for ``renderer.render()``

* **v0.0 (8/2/21)**

  * started project
  * documented JSON dictionary structure
