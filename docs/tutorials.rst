Tutorials
=========

Below is a set of tutorials to help you to build and render leaflet.js tiles.

1. Using the rendering script
2. Writing your own data
3. Writing your own skin file

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

Now, let's modify the data a bit. In ``data/examplepla.json``, you will find this:

.. code-block:: json
   "displayname": "Nowhere Express"

Replace that with:

.. code-block:: json
   "displayname": True

and run the renderer. You might encounter a Schema error:

.. code-block:: text

    TODO INSERT ERROR

We use Schema to check if the data is not corrupted and that it is in good shape.
If you see a Schema error, it means that the data has something wrong, not the renderer itself.
*(This might be very important when you write your own data in the future.)*

Remember to change the value back.
