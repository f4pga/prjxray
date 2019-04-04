.json Files
===========

Introduction
------------

This section documents how prjxray represents FPGA fabric. Its primarily composed of two files:
 * tilegrid.json: list of tiles and how they appear in the bitstream
 * tileconn.json: how tiles are connected together

General notes:
 * prjxray created names are generally lowercase, while Vivado created names are generally uppercase
 * _l and _r entries are generally identical, but probably represent different physical IP block layouts


tilegrid.json
-------------

This section assumes you are already familiar with the 7 series bitstream format.

This file contains two elements:
 * segments: each entry lists sections of the bitstream that encode part of one or more tiles
 * tiles: cores

segments
########

Segments are a prjxray concept.

Each entry has the following fields:
 * baseaddr: a tuple of (base address, inter-frame offset)
 * frames: how many frames are required to make a complete segment
 * words: number of inter-frame words required for a complete segment
 * tiles: which tiles reference this segment
 * type: prjxray given segment type

Sample entry:

.. code-block:: javascript

	"SEG_CLBLL_L_X16Y149": {
		"baseaddr": [
			"0x00020800",
			99
		],
		"frames": 36,
		"tiles": [
			"CLBLL_L_X16Y149",
			"INT_L_X16Y149"
		],
		"type": "clbll_l",
		"words": 2
	}

Interpreted as:
  * Segment is named SEG_CLBLL_L_X16Y149
  * Frame base address is 0x00020800
  * For each frame, skip the first 99 words loaded into FDRI
  * Since its 2 FDRI words out of possible 101, its the last 2 words
  * It spans across 36 different frame loads
  * The data in this segment is used by two different tiles: CLBLL_L_X16Y149, INT_L_X16Y149

Historical note:
In the original encoding, a segment was a collection of tiles that were encoded together.
For example, a CLB is encoded along with a nearby switch.
However, some tiles, such as BRAM, are much more complex. For example,
the configuration and data are stored in seperate parts of the bitstream.
The BRAM itself also spans multiple tiles and has multiple switchboxes.

tiles
#####

Each entry has the following fields:
 * grid_x: tile column, increasing right
 * grid_y: tile row, increasing down
 * segment: the primary segment providing bitstream configuration
 * sites: dictionary of sites name: site type contained within tile
 * type: Vivado given tile type

Sample entry:

.. code-block:: javascript

	"CLBLL_L_X16Y149": {
		"grid_x": 43,
		"grid_y": 1,
		"segment": "SEG_CLBLL_L_X16Y149",
		"sites": {
			"SLICE_X24Y149": "SLICEL",
			"SLICE_X25Y149": "SLICEL"
		},
		"type": "CLBLL_L"
	}

Interpreted as:
 * Located at row 1, column 43
 * Is configured by segment SEG_CLBLL_L_X16Y149
 * Contains two sites, both of which are SLICEL
 * A CLBLL_L type tile

tileconn.json
-------------

This file documents how adjacent tile pairs are connected.
No directionality is given.

The file contains one large list. Each entry has the following fields:
 * grid_deltas: (x, y) delta going from source to destination tile
 * tile_types: (source, destination) tile types
 * wire_pairs: list of (source tile, destination tile) wire names

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
 * Use when a CLBLL_L is above a HCLK_CLB (ie pointing south from CLBLL_L)
 * Connect CLBLL_L.CLBLL_LL_CIN to HCLK_CLB.HCLK_CLB_COUT0_L
 * Connect CLBLL_L.CLBLL_L_CIN to HCLK_CLB.HCLK_CLB_COUT1_L
 * A global clock tile is feeding into slice carry chain inputs

