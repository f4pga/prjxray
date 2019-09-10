"""
Add bits that are considered always on to the db file.

This script is Zynq specific.

There are three bits that are present in all Zynq bitstreams.
The investigation that was done to reach this conclusion is captured on GH
(https://github.com/SymbiFlow/prjxray/issues/746)
In brief, these bits seem to be bitstream properties related,
but no evidence of this could be found.
Due to the fact that the base address of these bits is the same as for the
CFG_CENTER_MID tile it has been decided to append the bits to its db file.
"""

import sys

constant_bits = {
    "CFG_CENTER_MID.ALWAYS_ON_PROP1": "26_2206",
    "CFG_CENTER_MID.ALWAYS_ON_PROP2": "26_2207",
    "CFG_CENTER_MID.ALWAYS_ON_PROP3": "27_2205"
}

with open(sys.argv[1], "a") as f:
    for bit_name, bit_value in constant_bits.items():
        f.write(bit_name + " " + bit_value + "\n")
