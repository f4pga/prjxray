# IOSTANDARD feature correlation minitest

This test checks which fasm features present in the db are set for given IO settings (IOSTANDARD + DRIVE + SLEW) and for which IOB type (IBUF, OBUF, IOBUF, IBUFDS, OBUFDS, IOBUFDS). It also checks what features are set on unused IOBs of a given bank in which active IOBs are instantiated. To avoid conflicts, a single iosettings combination is used within an IO bank.

## Running the minitest

1. Dump IOBs and generate verilog designs

`
make designs
`

2. (can skip this and go to 3) Synthesize designs, decode bitstreams to fasm files, correlate with database features

`
make analysis
`

3. Generate verilog and XML snippets to be used in cell definition, techmap and architecture definition
`
make snippets
`

## How it works

At first IOB information is dumped from Vivado. Relevant IOB attributes are: IO bank, is it a Vref input, is the IOB bonded.

Next a set of design is generated. Each design contains two IBUFs, two OBUFs and one IOBUF (if IOSTANDARD allows it) per bank.

These designs are synthesized and their bitstreams are disassembled to fasms.

Each fasm is compared agains the prjxray db to see what features are activated for given IO settings. Results of that checks are stored in CSV files which are then concatenated to one named "features.csv". Unknown bits are reported and stored in the "unknown_bits.jl" file.

The "features.csv" consists of one row per IO settings and one column per fasm feature. Each "cell" contains a string identifying for which types of IOB a given feature was active:
 - "I" input
 - "O" output
 - "T" inout
 - "U" active in unused IOBs of the same bank

Finally during code snippet generation the "feature.csv" file is read back by a python script and code snippets for cell definition, cell techmap and XML architecture definition are generated. The goal is to automatically generate mappings between parameters of Vivado's IOB cells to VPR IOB cells.

