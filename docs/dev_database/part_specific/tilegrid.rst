=============
tilegrid file
=============

The ``tilegrid.json`` is a list of all :term:`tiles <Tile>` in the device.
This information is used at various stages of the flow i.e. for
:term:`database <Database>` generation or creating a :term:`bitstream <Bitstream>`.
The most important parts of the file are related to :term:`frame <Frame>` addressing
within the :term:`bitstream <Bitstream>`, grid and :term:`clock region <Clock region>`
location, list of underlying :term:`sites <Site>`, or the type of the
:term:`tile <Tile>` itself.

Before diving into this section, it is advised to familiarize yourself with the
7-Series :doc:`Bitstream Format <../../architecture/bitstream_format>` chapter and
:doc:`Configuration <../../architecture/configuration>` chapter.

File format
-----------

The file consists of the entries describing every :term:`tile <Tile>` in
the FPGA chip. The file is of the form::

    {
        "<TILE_NAME>": {
            "bits": {
                "<CONFIGURATION_BUS>": {
                    "baseaddr": "<BASE_ADDR>,
                    "frames": 28,
                    "offset": 97,
                    "words": 2
                },
                <...>
        },
        "clock_region": <CLOCK_REGION>,
        "grid_x": <GRID_X>,
        "grid_y": <GRID_Y>,
        "pin_functions": {
            "<PIN_NAME">: "<PIN_FUNCTION>",
            <...>
        },
        "prohibited_sites": [
            "<SITE_TYPE>",
            <...>
        ],
        "sites": {
            "<SITE_NAME>": <SITE_TYPE>,
            <...>
        },
        "type": "INT_R"
    }

The ``<TILE_NAME>`` indicates the name of the :term:`tile <Tile>` described
in the entry. The naming convention matches Vivado.

Each :term:`tile <Tile>` entry in the file has the following fields:

- ``"bits"`` - contains the data related to :term:`tile <Tile>` configuration over
  the ``<CONFIGURATION_BUS>``. There are three types of the configuration
  buses in 7-Series FPGAs: ``CLB_IO_CLK``, ``BLOCK_RAM`` and ``CFG_CLB``.
  Every ``<CONFIGURATION_BUS>`` has the following fields:

   - ``baseaddr`` - Basic address of the configuration :term:`frame <Frame>`.
     Every configuration :term:`frame <Frame>` consist of 101 of 32bit
     :term:`words <Word>`. Note that a single :term:`frame <Frame>` usually configures
     a bunch of :term:`tiles <Tile>` connected to the single configuration bus.

   - ``"frames"`` - Number of :term:`frames <Frame>` that can configure the
     :term:`tile <Tile>`.

   - ``offset``   - How many words of offset is present in the :term:`frame <Frame>`
     before the first :term:`word <Word>` that configures the :term:`tile <Tile>`.

   - ``words``    - How many 32bit :term:`words <Word>` configure the :term:`tile <Tile>`.

- ``clock_region`` - indicates to which :term:`clock region <Clock region>` the
  :term:`tile <Tile>` belongs to.

- ``grid_x`` - :term:`tile <Tile>` column, increasing right

- ``grid_y`` - :term:`tile <Tile>` row, increasing down

- ``pin_functions`` - indicates the special functions of the :term:`tile <Tile>` pins.
  Usually it is related to IOB blocks and indicates i.e. differential output pins.

- ``prohibited_sites`` - Indicates which :term:`site <Site>` types cannot be used
  in the :term:`tile <Tile>`

- ``sites`` - dictionary which contains information about the :term:`sites <Site>`
  which can be found inside the :term:`tile <Tile>`. Every entry in
  the dictionary contains the following information:

   - ``"<SITE_NAME>"`` - The unique name of the :term:`site <Site>` inside
     the :term:`tile <Tile>`.

   - ``"<SITE_TYPE>`` - The type of the :term:`site <Site>`

- ``type`` - The type of the :term:`tile <Tile>`

Examples
--------

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

- :term:`Tile <Tile>` is named ``CLBLL_L_X16Y149``
- :term:`Frame <Frame>` base address is ``0x00020800``
- For each :term:`frame <Frame>`, skip the first 99 words loaded into FDRI
- Since it's 2 FDRI words out of possible 101, it's the last 2 words
- It spans across 36 different :term:`frame <Frame>` loads
- Located in :term:`clock region <Clock region>` ``X0Y2``
- Located at row 1, column 43
- Contains two :term:`sites <Site>`, both of which are SLICEL
- Is a ``CLBLL_L`` type :term:`tile <Tile>`


More information about :term:`frames <Frame>` and the FPGA configuration can be found in the
:doc:`Configuration <../../architecture/configuration>` chapter.
Example of absolute :term:`frame <Frame>` address calculation can be found in the
:doc:`mask file <../common/mask>` chapter.
