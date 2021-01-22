Display Port minitest
=====================

This minitest is a good test for the Gigabit Transcievers (GTP tiles) documentation process.

The test uses the [Hamsternz's Display Port](https://github.com/hamsternz/DisplayPort_Verilog) as a third party project.

To run the whole flow to generate the final FASM file run:

```bash
make all
```

To run the same flow, but with Yosys synthesis, run:

```bash
make all SYNTH=yosys
```

All the pre-requisites (LiteX, Yosys, etc.) are automatically installed/built. It is required though to have Vivado installed in the system.
