=============
tileconn file
=============

The ``tileconn.json`` file contains the information on how the wires of
neighboring tiles are connected. It contains one entry for each pair of
tile types, each containing a list of pairs of wires that belong to the same node.

.. warning:: FIXME: This is a good place to add the tile wire, pip, site pin diagram.

This file documents how adjacent tile pairs are connected.
No directionality is given.

File format
-----------

The file contains one large list::

    [
        {
            "grid_deltas": [
                <DELTA_X>,
                <DELTA_Y>
            ],
            "tile_types": [
                "<SOURCE_TILE>",
                "<DESTINATION_TILE>"
            ],
            "wire_pairs": [
                [
                    "<SOURCE_TILE_WIRE>",
                    "<DESTINATION_FILE_WIRE>"
                ],
                <...>
            ],
        },
        <...>
    ]

Each entry has the following fields:

- ``grid_deltas`` - indicates the position (``<DELTA_X>``, ``<DELTA_Y>``) of
  the source tile relative to the destination_file
- ``tile_types`` - contains the information about both
  ``<SOURCE_TILE_TYPE>`` and ``<DESTINATION_TILE_TYPE>``
- ``wire_pairs`` - contains the names of both
  ``<SOURCE_TILE_WIRE>`` and ``<DESTINATION_TILE_WIRE>``

Example
-------

.. code-block:: javascript

	{
		"grid_deltas": [
			0,
			1
		],
		"tile_types": [
			"CLBLL_L",
			"HCLK_CLB"
		],
		"wire_pairs": [
			[
				"CLBLL_LL_CIN",
				"HCLK_CLB_COUT0_L"
			],
			[
				"CLBLL_L_CIN",
				"HCLK_CLB_COUT1_L"
			]
		]
	}

Interpreted as:

- Use when a ``CLBLL_L`` is above a ``HCLK_CLB`` (i.e. pointing south from ``CLBLL_L``)
- Connect ``CLBLL_L.CLBLL_LL_CIN`` to ``HCLK_CLB.HCLK_CLB_COUT0_L``
- Connect ``CLBLL_L.CLBLL_L_CIN`` to ``HCLK_CLB.HCLK_CLB_COUT1_L``
- A global clock tile is feeding into slice carry chain inputs
