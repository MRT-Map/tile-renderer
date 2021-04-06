Formats
=======

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

Nodes (Note: Nodes != Points)
-----------------------------

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