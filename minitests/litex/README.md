# Minitest for LiteX desgin

This test generates LiteX SoC design which utilizes VexRiscV CPU, DDR memory and Ethernet. The design is implemented using both Yosys+Vivado and Vivado only flow. Output bitstream(s) is then processed using bit2fasm utility which allows to identify missing degbits.

