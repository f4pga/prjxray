# LiteX minitest

This folder contains a minitest for a Linux capable LiteX SoC for Arty board.

There are two variants: for Vivado only flow and for Yosys+Vivado flow. In order to run one of them enter the specific directory and run `make`.

The SoC "gateware" files were generated using the command:

```
./arty.py --cpu-type vexriscv --cpu-variant linux --with-ethernet --no-compile-software --no-compile-gateware
```
