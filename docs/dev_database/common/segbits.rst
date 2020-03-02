=============
segbits files
=============

The *segbits files* are generated for every FPGA :term:`tile <tile>` type.
They store the information about the combinations of bits in the bitstream
that are responsible for enabling different features inside the :term:`tile <tile>`.
The features can be related to enabling some part of the primitive, setting some
initial state of the block, configuring pin pull-up on output pins, etc.

Naming convention
-----------------

The naming scheme for the segbits files is the following::

   segbits_<tile>.db

Note that auxiliary ``segbits_<tile>.origin_info.db`` files
provide additional information about the :term:`fuzzer <fuzzer>`, which produced the
:term:`database <database>` file. This file is optional.

Every :term:`tile <tile>` is configured at least by one of three configurational buses
mentioned in the :doc:`Configuration Section <../../architecture/configuration>`.
The default bus is called ``CLB_IO_CLK``. If the :term:`tile <tile>` can also be configured
by another bus, it has additional ``segbits_<tile>.<bus_name>.db``
related to that bus.


Exemplary files:

   - ``segbits_dsp_r.db``
   - ``segbits_bram_l.db`` (configured with default ``CLB_IO_CLK`` bus)
   - ``segbits_bram_l.block_ram.db`` (configured with ``BLOCK_RAM`` bus)

File format
-----------

The file consists of the lines, containing the information about the feature
and the list of bits that should be enabled/disabled to provide the feature's
functionality::

   <feature> <bit_list>

where:

   - ``<feature>`` is of the form ``<feature_name>.<feature_addr>``
   - ``<bit_list>`` is the list of bits. Each bit is of the form
     ``<frame_address_offset>_<bit_possition>``. If the bit has the ``!``
     mark in front of it, that means it should be set to **0** for feature configuration,
     otherwise it should be set to **1**.

The names of the features are arbitrary. However, we named them in the convention,
which allows us to identify them quickly and provides suggestions
about the functionality that they provide. The feature names are used in the
fasm files generation.


Feature naming conventions
--------------------------

PIPs
^^^^

The ``<feature>`` names for interconnect :term:`PIPs <pip>` are stored in the
``segbits_int_l.db`` and ``segbits_int_r.db`` database files. The features that
enable interconnect :term:`PIPs <pip>` have the following syntax::

 <tile_type>.<destination_wire>.<source_wire>.

For example, consider the following entry in ``segbits_int_l.db``::

   INT_L.NL1BEG1.NN6END2 07_32 12_33

CLBs
^^^^
The ``<feature>`` names for CLB tiles use a dot-separated hierarchy.

For example::

   CLBLL_L.SLICEL_X0.ALUT.INIT[00]

This entry documents the initialization bits the *LSB LUT* for the *ALUT* in
the *SLICEL_X0* within a *CLBLL_L tile.*

Example
-------

Below there is a part of ``segbits_liob33_l.db`` file for the *artix7*
architecture. The file describes *CLBLL* :term:`tile <tile>`::

   <...>
   LIOB33.IOB_Y0.IBUFDISABLE.I 38_82
   LIOB33.IOB_Y0.IN_TERM.NONE !38_120 !38_122 !39_121 !39_123
   LIOB33.IOB_Y0.IN_TERM.UNTUNED_SPLIT_40 38_120 38_122 39_121 39_123
   LIOB33.IOB_Y0.IN_TERM.UNTUNED_SPLIT_50 38_120 38_122 !39_121 39_123
   LIOB33.IOB_Y0.IN_TERM.UNTUNED_SPLIT_60 38_120 !38_122 !39_121 39_123
   LIOB33.IOB_Y0.INTERMDISABLE.I 39_89
   LIOB33.IOB_Y0.LVTTL.DRIVE.I24 38_64 !38_112 !38_118 38_126 39_65 39_117 39_119 !39_125 !39_127
   LIOB33.IOB_Y0.PULLTYPE.KEEPER 38_92 38_94 !39_93
   LIOB33.IOB_Y0.PULLTYPE.NONE !38_92 38_94 !39_93
   LIOB33.IOB_Y0.PULLTYPE.PULLDOWN !38_92 !38_94 !39_93
   LIOB33.IOB_Y0.PULLTYPE.PULLUP !38_92 38_94 39_93
   <...>

In example, the line::

   LIOB33.IOB_Y0.PULLTYPE.PULLUP !38_92 38_94 39_93

means that the feature ``LIOB33.IOB_Y0.PULLTYPE.PULLUP`` will be set by clearing
bit ``!38_92`` and setting bits ``38_94`` and ``39_93``.

Generally, ``<feature>`` name is connected with its functionality.
In example, ``LIOB33.IOB_Y0.PULLTYPE.PULLUP`` means that in the LIOB33
:term:`tile <tile>`,
in IOB_Y0 site the *pull type* will be set to *PULLUP*.
This simply means that all pins belonging to this particular IOB
will be configured with pull-up.
