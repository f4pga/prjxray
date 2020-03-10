=============
tileconn file
=============

The file ``tileconn.json`` contains the information how the wires of neighboring
tiles are connected to each other. It contains one entry for each pair of tile
types, each containing a list of pairs of wires that belong to the same node.

.. warning:: FIXME: This is a good place to add the tile wire, pip, site pin diagram.

This file documents how adjacent tile pairs are connected.
No directionality is given.

The file contains one large list. Each entry has the following fields:

- ``grid_deltas`` - (x, y) delta going from source to destination tile
- ``tile_types`` - (source, destination) tile types
- ``wire_pairs`` - list of (source tile, destination tile) wire names

Sample entry:

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
