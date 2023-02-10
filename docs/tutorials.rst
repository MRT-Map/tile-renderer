Tutorials
=========

**Note: horrendously outdated**

Below is a set of tutorials to help you to build and render leaflet.js tiles.

1. Using the rendering script
2. The other functions
3. Writing your own data
4. Writing your own skin file

Using the rendering script
--------------------------

First steps
^^^^^^^^^^^

Download/clone the repository on Github. Then, copy over ``renderer.py``, ``data``, and ``skins`` into your project directory.
In a python file in the same directory, import the renderer:

.. code-block:: python

   import renderer

Now, you need to extract the data from the JSON files. I like to do it in a function:

.. code-block:: python

   def readFile(dir): # extract from JSON as dict
    with open(dir, "r") as f:
        data = json.load(f)
        f.close()
        return data

To test that it works:

.. code-block:: python

   print(readFile("data/examplepla.json"))

Now, render the tiles:

.. code-block:: python

   renderer.render(exampleplaRead(), examplenodesRead(), skinFileRead(), 1, 2, 8, saveDir="tiles/")
   pla = readFile("data/pla.json")
   nodes = readFile("data/nodes.json")
   skin = readFile("skins/default.json")
   
   renderer.render(pla, nodes, skin, 1, 2, 8)

You might be wondering what the "1, 2, 8" at the back mean.

* 1 is the minimum zoom level that the renderer will generate.
* 2 is the maximum zoom level that the renderer will generate.
* 8 is the number of units that a maximum zoom level tile will cover.

The number of units that a tile would cover is determined by d*2^z,
where d is the number of units that a tile of the maximum zoom would cover,
and z is the maximum zoom minus the current zoom level.
In this case, a tile of zoom 2 would cover 8 units, and a tile of zoom 1 would cover 16 units.
Note that the tile size stays the same, but the scale is doubled for each zoom out.

Data errors
^^^^^^^^^^^

Now, let's modify the data a bit. In ``data/examplepla.json``, you will find this:

.. code-block:: json

   "displayname": "Nowhere Express"

Replace that with:

.. code-block:: json

   "displayname": true

and run the renderer. You might encounter a Schema error:

.. code-block:: text

   schema.SchemaError: Key 'line' error:
   Key 'displayname' error:
   True should be instance of 'str'

We use Schema to check if the data is not corrupted and that it is in good shape.
If you see a Schema error, it means that the data has something wrong, not the renderer itself.
*(This might be very important when you write your own data in the future.)*

Remember to change the value back.

Preferences
^^^^^^^^^^^

You might have noticed that the renderer floods your main directory with tile images.
Fortunately, there is an option to save images in a separate folder.
For example, if you want to save the folder in ``tiles/``, just add this to the end of all existing arguments:

.. code-block:: python

   saveDir="tiles/"

The slash at the end is very important.
If you forget the slash, it will save all the tiles with the name "tilesZ, X, Y.png" in the main directory.

If you want to disable saving images entirely, set ``saveImages`` to False:

.. code-block:: python

   saveImages=False

By default, the skins are saved in ``skins/``. Skins contain icons which are pulled out from an asset folder.
The default folder is ``skins/assets/``. However, if for some reason you decide to relocate your skin folder to another area,
although the skin JSON file can be moved easily as the argument for it requests a dict and not a directory,
the renderer will still think the assets folder is still ``skins/assets/``.
To fix this, add this to the end of all existing arguments:

.. code-block:: python

   assetsDir="path_to_assets/"

Once again, remember the slash at the end.

Currently, when you run the script, you would see green and white-coloured logs.
If you don't want the white logs, add this:

.. code-block:: python

   verbosityLevel=0

This will suppress all the white logs, hence only showing the green ones.

The hierachy of logs are as follows:

* 0 - Green, logs important information, eg when a tile has finished rendering
* 1 - White, logs semi-important information, eg when a step of a PLA has been rendered
* 2 - White/Grey (bash), logs information about the process, eg when a new dash has been rendered

To suppress all logs, set ``verbosityLevel`` to -1.

Lastly, let's say you want only certain tiles to be rendered, in this case the tile ``1, 0, 0``.
Just add this to the end of all existing arguments:

.. code-block:: python

   tiles=[(1, 0, 0)]

Since it is a list, you can state multiple tiles.

.. code-block:: python

   tiles=[(1, 0, 0), (2, 0, 0)]

If you don't state the ``tiles`` argument, the renderer will automatically calculate which tiles to be rendered for you.

The other functions
-------------------

Other than ``renderer.render()``, the renderer has other functions.
For example, if you don't want leaflet.js tiles, ``renderer.tile_merge()`` is useful for merging tiles together.