# Minitests for SRLs

This is a minitest for various SRL configurations.

Uses Yosys to generate EDIF which is then P&R'd by Vivado.
The makefile also invokes `xc_fasm.bit2fasm` and `segprint`.
