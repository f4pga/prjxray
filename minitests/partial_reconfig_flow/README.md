# FASM Proof of Concept using Vivado Partial Reconfig flow

top.v is a top-level design that routes a variety of signal into a black-box
region of interest (ROI).  Vivado's Partial Reconfiguration flow (see UG909
and UG947) is used to implement that design and obtain a bitstream that
configures portions of the chip that are currently undocumented.

Designs that fit within the ROI are written in FASM and merged with the above
harness into a bitstream with fasm2frame and xc7patch.

# Usage

make rules are provided for generating each step of the process so that
intermediate forms can be analyzed.  Assuming you have a .fasm file, invoking
the %.hand\_crafted.bit rule will generate a merged bitstream:

```
make foo.hand\_crafted.bit # reads foo.fasm
```

# Using Vivado to generate .fasm

Vivado's Partial Reconfiguration flow can be used to synthesize and implement a
design that is then converted to .fasm.  The basic process is to write a module
that _exactly_ matches the roi blackbox in the top-level design.  Note that
even the name of the module must match exactly.  Once you have a design, the
first step is to synthesize the design with -mode out\_of\_context:

```
read_verilog <design>.v
synth_design -mode out_of_context -top roi -part $::env(XRAY_PART)
write_checkpoint -force <design>.dcp
```

Next, implement that design within the harness.  Run 'make harness\_routed.dcp'
if it doesn't already exist.  The following TCL will load the fully-routed
harness, load your synthesized design, and generate a bitstream containing
both:
```
open_checkpoint -force harness_routed.dcp
read_checkpoint -cell <design>.dcp
opt_design
place_design
route_design
write_checkpoint -force <design>_routed.dcp
write_bitstream -force <design>_routed.bit
```

'make <design>\_routed.fasm' will run a sequence of tools to extract the bits
that are inside the ROI and convert them to FASM.  The resulting .fasm can be
used to generate a marged bitstream using
'make <design>\_routed.hand\_crafted.bit'.  The resulting bitstream should be
equivalent to <design>\_routed.bit.
