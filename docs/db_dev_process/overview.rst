Overview
=========

SymbiFlow/symbiflow-arch-defs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This is where we describe the logical components in a device to VPR.

* VtR stands for `Verilog to Routing <https://verilogtorouting.org/>`_,
* VPR stands for VtR Place and Route.
* VtR also has its own synthesis tool called ODIN-II, but we are using `Yosys <https://github.com/YosysHQ/yosys>`_ instead of that.
  

Fuzzers
^^^^^^^
Fuzzers are things that generate a design, feed it to Vivado, and look at the resulting bitstream to make some conclusion.
This is how the contents of the database are generated.

The general idea behind fuzzers is to pick some element in the device (say a block RAM or IOB) to target.
If you picked the IOB (no one is working on that yet), you'd write a design that is implemented in a specific IOB.
Then you'd create a program that creates variations of the design (called specimens) that vary the design parameters, for example, changing the configuration of a single pin.

A lot of this program is TCL that runs inside Vivado to change the design parameters, because it is a bit faster to load in one Verilog model and use TCL to replicate it with varying inputs instead of having different models and loading them individually.

By looking at all the resulting specimens, you can correlate which bits in which frame correspond to a particular choice in the design.

Looking at the implemented design in Vivado with "Show Routing Resources" turned on is quite helpful in understanding what all choices exist.

.. toctree::
   :maxdepth: 1
   :caption: Current Fuzzers
   :glob:

   fuzzers/*

Minitests
^^^^^^^^^

Minitests are experiments to figure out how things work. They allow us to understand how to better write new fuzzers.

.. toctree::
   :maxdepth: 1
   :caption: Current Minitests
   :glob:

   minitests/*

Tools
^^^^^

`SymbiFlow/prjxray/tools/`

Here, you can find various programs to work with bitstreams, mainly to assist building fuzzers.

SymbiFlow/prjxray/minitests/roi_harness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Shows how to use a bunch of tools together to patch an existing bitstream with hand-crafted FASM (FPGA assembler).
