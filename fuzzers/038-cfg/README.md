# cfg fuzzer

This fuzzer solves some of the bits in the CFG_CENTER_MID tile
The tile contains sites of the following types: BSCAN, USR_ACCESS, CAPTURE, STARTUP, FRAME_ECC, DCIRESET and ICAP.
DCIRESET and USR_ACCESS don't really have any parameters.
The parameters on CAPTURE and FRAME_ECC don't toggle any bits in the bitstream.
