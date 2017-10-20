#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design_%s.bits" % sys.argv[1])

print("Loading tags from design_%s.txt." % sys.argv[1])
with open("design_%s.txt" % sys.argv[1], "r") as f:
    for line in f:
        line = line.split()
        site = line[0]
        bel = line[1]
        ctype = line[2]
        init = int(line[3][3])
        cinv = int(line[4][3])

        segmk.addtag(site, "%s.ZINI" % bel, 1-init)
        # segmk.addtag(site, "%s.CLOCK_INV" % (bel.split(".")[0]), cinv)

segmk.compile()
segmk.write(sys.argv[1])

