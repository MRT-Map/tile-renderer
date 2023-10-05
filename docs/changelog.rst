Changelog
=========
* **v4.0.1 (5/10/23)**

  * upgrade dependencies

* **v4.0.0 (20/4/23)**

  * chang antialias method
  * replace most function parameters with a single ``Config`` class
  * new ``Vector`` class
  * ``ImageCoord`` now saves coordinates as floats instead of integer, to reduce rounding errors
  * multiprocess file-dumping of preparation, and part 2
  * rewrite ``math_tools.dash()``
  * fix texts overlapping and texts around corners... maybe
  * move rendering operations counting from part 1 to preparation stage
  * new arrows on one-way lines
  * now uses Ruff, a linter in addition to mypy
  * reimplement AreaBorderTexts
  * fix off-centered text on areas
  * optimisations here and there

* **v3.0.0 (10/2/23)**

  * Add NotoSans and NotoSans-SC to rendering typefaces
  * Fix parts of the default skin
  * Lots of API changes, reorganisation and refactoring
  * Now uses ``rich`` to print logs and progress bars
  * Migrate project to use Poetry
  * Each Ray task now renders multiple tiles at once instead of one per task
  * Builders are now removed (use stencil instead!)
  * Implement PLA2 format
  * Add PLA1 to PLA2 converter
  * Project now uses ``pre-commit``
  * ``temp`` file is now moved out of package to present working directory
  * Image is now a ``webp`` instead of a ``png``
  * Task managers for parallel parts 1 and 3
  * Images are now antialised
  * Replace ``pickle`` with ``dill``
  * Further fix text overlapping
  * Attempts to fix diagonal text offsets (may not be working :( )
  * ``mypy`` is now used for better type checking
  * Docs are now working again

* **v2.2 (13/5/22)**

  * Multiline text is now centered
  * Improve skin, especially for small zooms
  * implement memory swapping for images to reduce RAM usage

* **v2.1 (6/4/22)**

  * Added SkinBuilder, a utility class for building skins Pythonically
  * Moved bulk of rendering code to ComponentStyle classes
  * Redid stud drawing
  * Fix text overlapping with _prevent_text_overlap
  * most mathtools functions now use WorldCoord and TileCoord
  * logging improvements
  * _TextObjects now store their bounds instead of their width/heights
  * new dashing algorithm ``mathtools.dash()``
  * offset function ``mathtools.offset()``
  * redid rendering for LineText so that they can go around corners
  * fixed arrow offset
  * debug switch to show additional debug Information
  * tweaked skin

* **v2.0 (23/12/21)**

  * "PLA" is no longer defined as "a set of components" but a file type (`.pla`)

    * Components are called... Components
    * Component JSON files have a ``.comps.pla`` suffix
    * Node JSON files have a ``.nodes.pla`` suffix

  * The CLI format has changed substantially to follow PEP8 naming conventions
  * The entire codebase has been reformatted to follow PEP8 naming conventions
  * Skins, components and nodes (& their list counterparts) now have their own classes, to make the code cleaner
  * Coords and TileCoords are now NamedTuples
  * ``pathlib.Path`` is now being used instead of raw strings
  * Ray multiprocessing integration (3.8 and 3.9 only)
  * Text rendering is now separated from the main rendering task
  * Rendering logs will no longer use the same line but rather will output one log per line
  * Builders:

    * Default IDs can now be set

      * PyAutoGUI is now used to automatically write the default ID

    * Commands now start with "."
    * ... and many more I probably forgot lol

  * ``internals.internal`` is now typed
  * Loggers and texts (for later rendering) now have their own private classes
  * Several functions in ``mathtools`` (``lines_intersect``, ``point_in_poly``, ``poly_center``) are now quicker to run (mostly using NumPy)

    * SymPy is no longer a dependency (yey)

  * ``misc`` no longer exists (``misc.getSkin`` is now ``Skin.from_name``)
  * ``tools`` is now split up into 6 files
  * Many functions in ``validate`` are now in their respective object classes
  * Made the CLI actually work (:P)

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
  * New function, ``renderer.validate.vGeoJson()``

    * ``renderer.validate.vCoords()`` now supports lists along with tuples

  * The renderer now has a CLI, to show the help page do ``python -m renderer -h``
  * ``renderer.render()`` now supports float maxZoomRanges
  * New functions: ``renderer.tools.plaJson.toGeoJson()`` and ``renderer.tools.geoJson.toNodePlaJson()``

    * these are for translating our custom format of storing geographical format to geoJson
    * (btw why we're not using geoJson is because its harder to store nodes)

  * internal-use files have been moved to ``renderer/internals/``
  * removed ``renderer.tools.plaJson.toTiles()`` as it's a duplicate of ``renderer.tools.plaJson.renderedIn()``
  * ``renderer.tools.coord.toTiles()`` now supports tuples as ``coords`` parameter

* **v1.1 (2/5/21)**

  * Added log prefixes to ``renderer.render()`` and ``renderer.tileMerge()``
  * Improved curved line drawing
  * ``renderer.py`` is now split into a package

    * ``renderer.utils`` renamed to ``renderer.validate``
    * all functions of ``renderer.tools`` and ``renderer.validate`` renamed
    * method descriptions added to all functions except those in ``renderer.internal``

  * New function: ``renderer.misc.getSkin()``
  * New logging system that does not clog your terminal
  * changed colour library from ``colorama`` to ``blessed``
  * fixed ``renderer.mergeTiles()``, especially in determining which zooms to merge and retrieving images
  * fixed ``renderer.misc.getSkin()``

* **v1.0 (13/4/21)**

  * added stripes for areas
  * added offset for image centertext
  * new function: ``renderer.tools.line_findEnds()``
  * new function: ``renderer.mathtools.pointsAway()``

    * replaces the messy and unresponsive find-two-points-n-units-away-from-a-point-on-a-straight-line calculations of sympy using trigo
    * rendering should be faster now (``renderer.render.midpoint()``'s speed is now 0-1% of the original speed)
    * **REJECT SYMPY, EMBRACE TRIGONOMETRY, ALL HAIL TRIGO**

  * added a few more level 2 logs to ``renderer.render()``
  * new function: ``renderer.tileMerge()``, used to merge tiles
  * changed output of ``renderer.render()`` from list to dict
  * in counting of rendering operations in ``renderer.render()``, added 1 to each tilePlas to account for text
  * rewrote ``renderer.mathtools.dash()`` and ``renderer.mathtools.dashOffset()``, they're no longer broken :D
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
  * added ``renderer.mathtools.dashOffset()``
  * fixed dashed roads
  * bounding boxes on texts so they don't overlap
  * new logging function (``renderer.internal.log()``)

    * ``renderer.render()`` has new ``verbosityLevel`` optional argument, defaults to 1

  * estimated that last beta release before v1.0 is v0.8 or v0.9

* **v0.6 (11/3/21)**

  * added loads of PLAs to the default skin; there are now about 90 different PLA types :))
  * tweaked ``renderer.mathtools.midpoint()`` a bit
  * new functions: ``renderer.mathtools.polyCenter()``, ``renderer.mathtools.dash()``
  * Moved ``renderer.tools.lineInBox()`` to ``renderer.mathtools.lineInBox()``
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
  * Added functions ``renderer.mathtools.midpoint()``, ``renderer.mathtools.linesIntersect()``, ``renderer.mathtools.pointInPoly()``, ``renderer.tools.lineInBox()``, ``renderer.tools.lineInBox()``, ``findPlasAttachedToNode()``
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
    * ``renderer.internal.tupleToStr()``
    * ``renderer.internal.strToTuple()``
    * ``renderer.internal.readJson()``
    * ``renderer.internal.writeJson()``
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