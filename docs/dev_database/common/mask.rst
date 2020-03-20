==========
mask files
==========

The *mask files* are generated for every FPGA :term:`tile <Tile>` type.
They store the information which bits in the bitstream can configure the given
:term:`tile <Tile>` type.

Naming convention
-----------------

The naming scheme for the mask files is the following::

   mask_<tile>.db

Note that auxiliary ``mask_<tile>.origin_info.db`` files
provide additional information about the :term:`fuzzer <Fuzzer>`,
which produced the :term:`database <Database>` file. This file is optional.

Every :term:`tile <Tile>` is configured at least by one of three configurational
buses mentioned in the :doc:`Configuration Section <../../architecture/configuration>`.
The default bus is called ``CLB_IO_CLK``.
If the :term:`tile <Tile>` can also be configured by another bus, it has an additional ``mask_<tile>.<bus_name>.db``
related to that bus.

For example:

   - ``mask_dsp_r.db``
   - ``mask_bram_l.db`` (configured with default ``CLB_IO_CLK`` bus)
   - ``mask_bram_l.block_ram.db`` (configured with ``BLOCK_RAM`` bus)

File format
-----------

The file consists of records that describe the configuration bits for
the particular :term:`tile <Tile>` type. Each entry inside the file is of the form::

   bit <frame_address_offset>_<bit_position>

This means that the :term:`tile <Tile>` can be configured by a bit located in the
:term:`frame <Frame>` at the address ``<base_frame_addr> + <frame_address_offset>``,
at position ``<tile_offset> + <bit_position>``. Information about ``<base_frame_address>``
and ``<tile_offset>`` can be taken from part specific ``tilegrid.json`` file.

Example
-------

Below there is a part of artix7 ``mask_clbll_l.db`` file describing a FPGA *CLBLL*
:term:`tile <Tile>`::

   <...>
   bit 00_61
   bit 00_62
   bit 00_63
   bit 01_00
   bit 01_01
   bit 01_02
   <...>

The line ``bit 01_02`` means that the *CLBL_LL* :term:`tile <Tile>` can be
configured by the bit located in the :term:`frame <Frame>` at the address
``<base_frame_address> + 0x01``, at position ``<tile_offset> + 0x2``.

The ``tilegrid.json`` is a file specific to a given chip package.
For *xc7a35tcpg236-1* we can find an exemplary *CLBLL_L* entry::

    "CLBLL_L_X2Y0": {
        "bits": {
            "CLB_IO_CLK": {
                "baseaddr": "0x00400100",
                "frames": 36,
                "offset": 0,
                "words": 2
            }
        },
        "clock_region": "X0Y0",
        "grid_x": 10,
        "grid_y": 155,
        "pin_functions": {},
        "sites": {
            "SLICE_X0Y0": "SLICEL",
            "SLICE_X1Y0": "SLICEL"
        },
        "type": "CLBLL_L"
    },

The ``<base_frame_addr>`` can be found as a argument of the *"baseaddr"* key
and for *CLBLL_L_X2Y0* :term:`tile <Tile>` it is equal to ``0x00400100``. The ``<tile_offset>``
on the other hand is an argument of the *"offset"* key. Here it is equal to 0.

Finally, we are able to compute the bit location associated with the
``bit 01_02`` entry.

The configuration bit for this record can be found in the following
:term:`frame <Frame>` address::

   0x00400100 + 0x01 = 0x00400101

Located at the bit position::

   0x0 + 0x2 = 0x2

More about the configuration process and the meaning of the :term:`frame <Frame>`
can be found in the :doc:`Configuration Section <../../architecture/configuration>`.
