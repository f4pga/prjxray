# BEL timings fuzzer

This fuzzer is suppose to extract all the BEL timings for Xilinx 7-series FPGAs.
The extracted timings are saved as SDF files.
Single SDF file is produced for every FPGA tile type.

## Fuzzer flow

Fuzzer flow is the following:

Vivado/`runme.tcl` -> `fixup_timings_txt.py` -> `tim2json.py` -> `makesdf.py` -> `sdfmerge.py`

The fuzzer uses Vivado tcl script to read all the FPGA timings data.
This data is dumped to a text file.
Beside timings data the tcl scipt dumps the following information:

* Sites pins
* BELs pins
* BELs attributes

The tcl script iterates over every BEL for all the sites in each tile type.
The timings, pins and attributes are dumped in the same hierarchy.
This hierarchy is used by the `tim2json` script to process the txt dump.
Main task of the `tim2json` script is to figure out what the dumped timings mean and what paths do they describe.
This is done by parsing the string timings, searching the BEL/Sites pins and BEL attributes.
Since for some pins there was no naming convention, the names are provided directly via `pin_alias_map.json`.

Some BELs (e.g. BRAMs) reports the timings with incorrect site name.
To work around this issue the `fixup_timings_txt.py` script is used to flatten the timings dump file.
As a result all the timings for a selected tile are squashed into one site.

### Text files format

The files dumped by the Vivado scrips have the following format:

Each line starts with a tile name, proceeded by a number of sites in the tile.
After the tiles count, each tile info is placed.
The tile info starts with a tile name followed by number of BELs in the tile.
The bels number is followed by BEL entries.
Each BEL entry starts with BEL name followed by a number of entries.
The entries differ between the file types:

* timings file: each timing entry starts with entry name followed by 5 timings values
* properties file: each properties entry starts with property name followed by a number of possible property values, followed by a list of the possible property values
* pins file: each pin entry starts with pin name, followed by pin direction (IN/OUT), followed by 0 or 1 flag saying if the pin is a clock pin
