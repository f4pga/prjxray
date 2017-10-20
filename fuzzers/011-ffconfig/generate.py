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

        if False:
            segmk.addtag(site, "%s.TYPE_%s" % (bel, ctype), 1)

            for i in range(1, 15):
                types = set()
                if i & 1: types.add("FDCE")
                if i & 2: types.add("FDPE")
                if i & 4: types.add("FDRE")
                if i & 8: types.add("FDSE")
                segmk.addtag(site, "%s.TYPES_%s" % (bel, "_".join(sorted(types))), ctype in types)

        if False:
            segmk.addtag(site, "%s.CLOCK_INV" % (bel.split(".")[0]), cinv)

        segmk.addtag(site, "%s.ZINI" % bel, 1-init)

segmk.compile()
segmk.write(sys.argv[1])

