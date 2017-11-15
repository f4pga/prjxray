#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

tiledata = dict()
pipdata = dict()

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        tile, pip, src, dst = line.split()
        _, pip = pip.split(".")
        _, src = src.split("/")
        _, dst = dst.split("/")

        if tile not in tiledata:
            tiledata[tile] = {
                "pips": set(),
                "srcs": set(),
                "dsts": set()
            }

        if pip in pipdata:
            assert pipdata[pip] == (src, dst)
        else:
            pipdata[pip] = (src, dst)

        tiledata[tile]["pips"].add(pip)
        tiledata[tile]["srcs"].add(src)
        tiledata[tile]["dsts"].add(dst)

for tile, pips_srcs_dsts in tiledata.items():
    pips = pips_srcs_dsts["pips"]
    srcs = pips_srcs_dsts["srcs"]
    dsts = pips_srcs_dsts["dsts"]

    for pip, src_dst in pipdata.items():
        src, dst = src_dst
        if re.match(r"^LVB?(_L)?[0-9]", src) or re.match(r"^LVB?(_L)?[0-9]", dst):
            continue
        if pip in pips:
            segmk.addtag(tile, "%s.%s" % (dst, src), 1)
        elif src_dst[1] not in dsts:
            segmk.addtag(tile, "%s.%s" % (dst, src), 0)

segmk.compile()
segmk.write()

