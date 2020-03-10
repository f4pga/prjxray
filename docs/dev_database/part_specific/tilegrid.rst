=============
tilegrid file
=============

The ``tilegrid.json`` is a list of all tiles in the device.
Each entry contains information related to the specific tile which is used at various stages of the database generation or bitstream creation.
The most important parts of the data are related to frame addressing within the bitstream, grid and clock region location, list of underlying sites or the type of the tile itself.
Before diving into this section it is advised to familiarize yourself with the 7 series :doc:`bitstream format <../../architecture/bitstream_format>` chapter.

tiles
-----

Each entry has the following fields:

- ``baseaddr`` - a tuple of (base address, inter-frame offset)
- ``frames`` - how many frames are required to make a complete segment
- ``offset`` - offset of the configuration word within the frame
- ``words`` - number of inter-frame words required for a complete segment
- ``clock_regions`` - the name of the clock region the tile resides in
- ``grid_x`` - tile column, increasing right
- ``grid_y`` - tile row, increasing down
- ``sites`` - dictionary of sites name: site type contained within tile
- ``type`` - Vivado given tile type

Sample entry:

.. code-block:: javascript

    "CLBLL_L_X16Y149": {
        "bits": {
            "CLB_IO_CLK": {
                "baseaddr": "0x00020800",
                "frames": 36,
                "offset": 99,
                "words": 2
            }
        },
        "clock_region": "X0Y2",
        "grid_x": 43,
        "grid_y": 1,
        "pin_functions": {},
        "sites": {
            "SLICE_X24Y149": "SLICEL",
            "SLICE_X25Y149": "SLICEL"
        },
        "type": "CLBLL_L"
    }

Interpreted as:

- Tile is named ``CLBLL_L_X16Y149``
- Frame base address is ``0x00020800``
- For each frame, skip the first 99 words loaded into FDRI
- Since it's 2 FDRI words out of possible 101, it's the last 2 words
- It spans across 36 different frame loads
- Located in clock region ``X0Y2``
- Located at row 1, column 43
- Contains two sites, both of which are SLICEL
- Is a ``CLBLL_L`` type tile

.. warning:: FIXME: We should cross link to how to use the base address and word offset.

