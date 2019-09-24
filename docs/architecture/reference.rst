References
==========

Xilinx documents one should be familiar with:
---------------------------------------------

### UG470: 7 Series FPGAs Configuration User Guide

https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf

*Chapter 5: Configuration Details* contains a good description of the overall
bit-stream format. (See section "Bitstream Composition" and following.)

### UG912: Vivado Design Suite Properties Reference Guide

http://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_3/ug912-vivado-properties.pdf

Contains an excellent description of the in-memory data structures and
associated properties Vivado uses to describe the design and the chip. The TCL
interface provides a convenient interface to access this information.

### UG903: Vivado Design Suite User Guide: Using Constraints

http://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_3/ug903-vivado-using-constraints.pdf

The fuzzers generate designs (HDL + Constraints) that use many physical
contraints constraints (placement and routing) to produce bit-streams with
exactly the desired features. It helps to learn about the available constraints
before starting to write fuzzers.

### UG901: Vivado Design Suite User Guide: Synthesis

http://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_3/ug901-vivado-synthesis.pdf

*Chapter 2: Synthesis Attributes* contains an overview of the Verilog
attributes that can be used to control Vivado Synthesis. Many of them
are useful for writing fuzzer designs. There is some natural overlap
with UG903.

### UG909: Vivado Design Suite User Guide: Partial Reconfiguration

https://www.xilinx.com/support/documentation/sw_manuals/xilinx2017_3/ug909-vivado-partial-reconfiguration.pdf

Among other things this UG contains some valuable information on how to constrain a design in a way so that the items inside a pblock are strictly separate from the items outside that pblock.

### UG474: 7 Series FPGAs Configurable Logic Block

https://www.xilinx.com/support/documentation/user_guides/ug474_7Series_CLB.pdf

Describes the capabilities of a CLB, the most important non-interconnect resource of a Xilinx FPGA.

Other documentation that might be of use:
-----------------------------------------

Doc of .bit container file format:
http://www.pldtool.com/pdf/fmt_xilinxbit.pdf

Open-Source Bitstream Generation for FPGAs, Ritesh K Soni, Master Thesis:
https://vtechworks.lib.vt.edu/bitstream/handle/10919/51836/Soni_RK_T_2013.pdf

VTR-to-Bitstream, Eddie Hung:
https://eddiehung.github.io/vtb.html

From the bitstream to the netlist, Jean-Baptiste Note and Éric Rannaud:
http://www.fabienm.eu/flf/wp-content/uploads/2014/11/Note2008.pdf

Wolfgang Spraul's Spartan-6 (xc6slx9) project:
https://github.com/Wolfgang-Spraul/fpgatools

Marek Vasut's Typhoon Cyclone IV project:
http://git.bfuser.eu/?p=marex/typhoon.git

XDL generator/imported for Vivado:
https://github.com/byuccl/tincr

