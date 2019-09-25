# FASM Proof of Concept using Vivado Partial Reconfig flow

harness.v is a top-level design that routes a variety of signal into a black-box
region of interest (ROI).  Vivado's Partial Reconfiguration flow (see UG909
and UG947) is used to implement that design and obtain a bitstream that
configures portions of the chip that are currently undocumented.

Designs that fit within the ROI are written in FASM and merged with the above
harness into a bitstream with fasm2frame and xc7patch.  Since writting FASM is
rather tedious, rules are provided to convert Verilog ROI designs into FASM via
Vivado.

## Usage

make rules are provided for generating each step of the process so that
intermediate forms can be analyzed.  Assuming you have a .fasm file, invoking
the %\_hand\_crafted.bit rule will generate a merged bitstream:

```
make foo.hand\_crafted.bit # reads foo.fasm
```

## Using Vivado to generate .fasm

Vivado's Partial Reconfiguration flow can be used to synthesize and implement a
ROI design that is then converted to .fasm.  Write a Verilog module
that _exactly_ matches the roi blackbox model in the top-level design.  Note
that even the name of the module must match exactly.  Assuming you have created
that design in my\_roi\_design.v, 'make my\_roi\_design\_hand\_crafted.bit'
will synthesize and implement the design with Vivado, translate the resulting
partial bitstream into FASM, and then generate a full bitstream by patching the
harness bitstream with the FASM.  non\_inv.v is provided as an example ROI
design for this flow.
