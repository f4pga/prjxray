============
Introduction
============

`Project X-Ray`_ documents the `Xilinx`_ 7-Series FPGA architecture to enable
the development of open-source tools.  Our goal is to provide sufficient information
to develop a free and open Verilog to bitstream toolchain for these devices.

The project is a part of SymbiFlow Toolchain. `SymbiFlow`_ uses the obtained
information about the chip in `Architecture Definitions`_ project, which
allows for creating bitstreams for many architectures including 7-Series devices.

Collected information
---------------------

To allow the usage of Xilinx FPGAs in SymbiFlow toolchain we collect some
important data about the Xilinx chips. The needed information includes:

   - Architecture description:

      * chip internals
      * timings

   - Bitstream format:

      * metadata (i.e. header, crc)
      * configuration bits

Final results are stored in the database which is further used by the
`Architecture Definitions`_ project. The whole database is described in
the dedicated :doc:`chapter <dev_database/index>`.

Methodology
-----------

The most important element of the project are fuzzers - scripts responsible
for obtaining information about the chips. Their name comes from the fact that
they use a similar idea to `Fuzz testing`_. Firstly, they generate a huge
amount of designs in which the examined chip property is either enabled or
disabled. By comparing the differences in the final bitstream obtained
from vendor tools, we can detect relations between bits in the bitstream and
provided functionalities.

However, some of the fuzzers works differently, i.e. they just creating
the database structure, the whole idea is similar and rely on the output produced
by the vendor tools.

All fuzzers are described in the dedicated :doc:`chapter <db_dev_process/fuzzers/index>`.

.. _Fuzz testing: https://en.wikipedia.org/wiki/Fuzzing

Important Parts
---------------

The important parts of the `Project X-Ray` are:

   - *minitests* - designs that can be viewed by a human in Vivado to better
     understand how to generate more useful designs.
   - *experiments* - similar to *minitests* except for the fact that they are only
     useful for a short time.
   - *tools & libs* - they convert the resulting bitstreams into various formats.
   - *utils* - tools that are used but still require some testing

.. _Project X-Ray: https://github.com/SymbiFlow/prjxray
.. _Xilinx: http://www.xilinx.com/
.. _SymbiFlow: https://symbiflow.readthedocs.io/
.. _Architecture Definitions: https://github.com/SymbiFlow/symbiflow-arch-defs
