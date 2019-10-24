# LiteX Litex BaseSoC + LiteDRAM minitest

This folder contains a minitest for the Litex memory controller (LiteDRAM).
For checking the memory interface we leverage the fact that the BIOS firmware performs a memory test at startup.
The SoC is a Basic LiteX SoC configuration for the Arty board with the VexRiscv core.

## Synthesis+implementation

There are two variants: for Vivado only flow and for Yosys+Vivado flow. In order to run one of them enter the specific directory and run `make`.
Once the bitstream is generated and loaded to the board, we should see the test result on the terminal connected to one of the serial ports.
