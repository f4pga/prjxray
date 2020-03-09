Fuzzers
=======

Fuzzers are a set of tests which generate a design, feed it to Vivado, and look at the resulting bitstream to make some conclusion.
This is how the contents of the database are generated.

The general idea behind fuzzers is to pick some element in the device (say a block RAM or IOB) to target.
If you picked the IOB, you'd write a design that is implemented in a specific IOB.
Then you'd create a program that creates variations of the design (called specimens) that vary the design parameters, for example, changing the configuration of a single pin.

A lot of this program is TCL that runs inside Vivado to change the design parameters, because it is a bit faster to load in one Verilog model and use TCL to replicate it with varying inputs instead of having different models and loading them individually.

By looking at all the resulting specimens, you can correlate which bits in which frame correspond to a particular choice in the design.

Looking at the implemented design in Vivado with "Show Routing Resources" turned on is quite helpful in understanding what all choices exist.

Configurable Logic Blocks (CLB)
-------------------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *clb*

Block RAM (BRAM)
----------------

.. toctree::
   :maxdepth: 1
   :glob:

   *bram*

Input / Output (IOB)
--------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *iob*

Clocking (CMT, PLL, BUFG, etc)
------------------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *clk*
   *cmt*

Programmable Interconnect Points (PIPs)
---------------------------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *pip*

Hard Block Fuzzers
------------------

.. toctree::
   :maxdepth: 1
   :glob:

   *xadc*

Grid and Wire
-------------

.. toctree::
   :maxdepth: 1
   :glob:

   tilegrid

All Fuzzers
-----------

.. toctree::
   :maxdepth: 1
   :glob:

   *
