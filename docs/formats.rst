Formats
=======
.. _formats:
PLAs
----
.. code-block:: javascript

  {
    "(nameid)": {
      "type": "(type)",
      "displayname": "(displayname)",
      "description": "(description)".
      "layer": layer_no,
      "nodes": [nodeid, nodeid, nodeid],
      "attrs": {
        "(attr name)": "(attr val)",
      // etc
      }
    },
    //etc
  }

Nodes
-----

**(Note: Nodes != Points)**

.. code-block:: javascript

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

*Note: Connections is not implemented yet*

Skins
-----

.. code-block:: javascript


   {
       "info": {
           "size": size,
           "font": {
               "": "(tff file location in assets)",
               "b": "(tff file location in assets)",
               "i": "(tff file location in assets)",
               "bi": "(tff file location in assets)"
           },
           "background": [r, g, b]
       },
       "order": [
           "(type)",
           "(type)",
           // etc
       ],
       "types": {
           "(type-point)": {
               "tags": [],
               "type": "point",
               "style": {
                   "(maxZ), (minZ)": [
                       {
                           "layer": "circle",
                           "colour": "(hex)" / null,
                           "outline": "(hex)" / null,
                           "size": size,
                           "width": width
                       },
                       {
                           "layer": "text",
                           "colour": "(hex)" / null,
                           "offset": [x, y],
                           "size": size,
                           "anchor": null / (anchor)
                       },
                       {
                           "layer": "square",
                           "colour": "(hex)" / null,
                           "outline": "(hex)" / null,
                           "size": size,
                           "width": width
                       },
                       {
                           "layer": "image",
                           "file": "(image file location in assets)",
                           "offset": [x, y]
                       }
                   ],
                   //etc
               }
           },
           "(type-line)": {
               "tags": [],
               "type": "line",
               "style": {
                   "(maxZ), (minZ)": [
                       {
                           "layer": "back",
                           "colour": "(hex)",
                           "width": width,
                           *"dash": [dashlength, gaplength] (Optional)*
                       },
                       {
                           "layer": "fore",
                           "colour": "(hex)",
                           "width": width,
                           *"dash": [dashlength, gaplength] (Optional)*
                       },
                       {
                           "layer": "text",
                           "colour": "(hex)",
                           "size": size,
                           "offset": offset
                       }
                   ],
                   //etc
               }
           },
           "(type-area)": {
               "tags": [],
               "type": "area",
               "style": {
                   "0, 5": [
                       {
                           "layer": "fill",
                           "colour": "(hex)",
                           "outline": "(hex)"
                       },
                       {
                           "layer": "bordertext",
                           "colour": "(hex)",
                           "offset": offset,
                           "size": size
                       },
                       {
                           "layer": "centertext",
                           "colour": "(hex)",
                           "size": size,
                           "offset": [x, y]
                       },
                       {
                           "layer": "centerimage",
                           "file": "(image file location in assets)",
                           "offset": [x, y]
                       }
                   ],
                   //etc
               }
           }
       }
   }
