
Fuzzers
=======
Fuzzers are things that generate a design, feed it to Vivado, and look at the resulting bitstream to make some conclusion.
This is how the contents of the database are generated.

The general idea behind fuzzers is to pick some element in the device (say a block RAM or IOB) to target.
If you picked the IOB (no one is working on that yet), you'd write a design that is implemented in a specific IOB.
Then you'd create a program that creates variations of the design (called specimens) that vary the design parameters, for example, changing the configuration of a single pin.

A lot of this program is TCL that runs inside Vivado to change the design parameters, because it is a bit faster to load in one Verilog model and use TCL to replicate it with varying inputs instead of having different models and loading them individually.

By looking at all the resulting specimens, you can correlate which bits in which frame correspond to a particular choice in the design.

Looking at the implemented design in Vivado with "Show Routing Resources" turned on is quite helpful in understanding what all choices exist.

Configurable Logic Blocks (CLB)
-------------------------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*clb*

Block RAM (BRAM)
----------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*bram*

Input / Output (IOB)
--------------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*iob*

Clocking (CMT, PLL, BUFG, etc)
------------------------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*clk*
   fuzzers/*cmt*

Programmable Interconnect Points (PIPs)
---------------------------------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*int*
   fuzzers/*pip*

Hard Block Fuzzers
------------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*xadc

Grid and Wire
-------------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/tilegrid
   fuzzers/tileconn
   fuzzers/ordered_wires
   fuzzers/get_counts
   fuzzers/dump_all

Timing
------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/timing

All Fuzzers
-----------

.. toctree::
   :maxdepth: 1
   :glob:

   fuzzers/*

Minitests
=========

Minitests are experiments to figure out how things work. They allow us to understand how to better write new fuzzers.

.. toctree::
   :maxdepth: 1
   :caption: Current Minitests
   :glob:

   minitests/*

Tools
=====

`SymbiFlow/prjxray/tools/`

Here, you can find various programs to work with bitstreams, mainly to assist building fuzzers.
