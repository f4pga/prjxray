#!/usr/bin/env python3

import sys, os, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design_%s.bits" % sys.argv[1])

pipdata = dict()
ignpip = set()

print("Loading tags from design.txt.")
with open("design_%s.txt" % sys.argv[1], "r") as f:
    for line in f:
        tile, loc, mask, pattern = line.split()
        dsp = "DSP_0" if loc[-1] in "02468" else "DSP_1"

        mask = int(mask.replace("48'h", ""), 16)
        pattern = int(pattern.replace("48'h", ""), 16)

        for i in range(48):
            segmk.add_tile_tag(tile, "%s.MASK[%d]" % (dsp, i), (mask >> i) & 1)
            segmk.add_tile_tag(
                tile, "%s.PATTERN[%d]" % (dsp, i), (pattern >> i) & 1)

segmk.compile()
segmk.write(suffix=sys.argv[1])
