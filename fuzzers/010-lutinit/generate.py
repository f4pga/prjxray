#!/usr/bin/env python3

import sys

from prjxray.segmaker import Segmaker
from prjxray import util

segmk = Segmaker(util.get_db_root(), "design_%s.bits" % sys.argv[1])

print("Loading tags from design_%s.txt." % sys.argv[1])
with open("design_%s.txt" % sys.argv[1], "r") as f:
    for line in f:
        line = line.split()
        site = line[0]
        bel = line[1]
        init = int(line[2][4:], 16)

        for i in range(64):
            bitname = "%s.INIT[%02d]" % (bel, i)
            bitname = bitname.replace("6LUT", "LUT")
            segmk.add_site_tag(site, bitname, ((init >> i) & 1) != 0)

segmk.compile()
segmk.write(sys.argv[1])
