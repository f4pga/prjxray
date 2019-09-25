.. Project X-Ray documentation master file, created by
   sphinx-quickstart on Mon Feb  5 11:04:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Project X-Ray
=========================================

`Project X-Ray`_ documents the `Xilinx`_ 7-Series FPGA architecture to enable
development of open-source tools.  Our goal is to provide sufficient information
to develop a free and open Verilog to bitstream toolchain for these devices.

.. _Project X-Ray: https://github.com/SymbiFlow/prjxray
.. _Xilinx: http://www.xilinx.com/

.. toctree::
   :maxdepth: 2
   :caption: Xilinx 7-series Architecture

   architecture/overview
   architecture/configuration
   architecture/bitstream_format
   architecture/interconnect
   architecture/dram_configuration
   architecture/glossary
   architecture/reference
   architecture/code_of_conduct
   architecture/updating_the_docs
   architecture/copying

.. toctree::
   :maxdepth: 2
   :caption: Database Development Process

   db_dev_process/readme
   db_dev_process/contributing
   db_dev_process/fuzzers/index
   db_dev_process/minitests/index
   db_dev_process/parts

.. toctree::
   :maxdepth: 2
   :caption: Output File Formats

   format/db
   format/tile
