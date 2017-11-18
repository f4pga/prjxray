#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

pipdata = dict()
ignpip = set()

def handle_design(prefix, second_pass):
    segmk = segmaker(prefix + ".bits")

    tiledata = dict()
    nlines = 0

    print("Loading tags from design.txt.")
    with open(prefix + ".txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()
            _, pip = pip.split(".")
            _, src = src.split("/")
            _, dst = dst.split("/")
            pnum = int(pnum)
            pdir = int(pdir)

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

            if pdir == 0:
                tiledata[tile]["srcs"].add(dst)
                tiledata[tile]["dsts"].add(src)

            if pnum == 1 or pdir == 0 or \
                    re.match(r"^(L[HV]B?)(_L)?(_B)?[0-9]", src) or \
                    re.match(r"^(L[HV]B?)(_L)?(_B)?[0-9]", dst) or \
                    re.match(r"^(CTRL|GFAN)(_L)?[0-9]", dst):
                ignpip.add(pip)

            nlines += 1

    if nlines == 0:
        return

    for tile, pips_srcs_dsts in tiledata.items():
        pips = pips_srcs_dsts["pips"]
        srcs = pips_srcs_dsts["srcs"]
        dsts = pips_srcs_dsts["dsts"]

        for pip, src_dst in pipdata.items():
            src, dst = src_dst
            if pip in ignpip:
                pass
            elif pip in pips:
                segmk.addtag(tile, "%s.%s" % (dst, src), 1)
            elif src_dst[1] not in dsts:
                segmk.addtag(tile, "%s.%s" % (dst, src), 0)

    if second_pass:
        segmk.compile()
        segmk.write(prefix[7:])

for arg in sys.argv[1:]:
    prefix = arg[0:-4]
    handle_design(prefix, False)

for arg in sys.argv[1:]:
    prefix = arg[0:-4]
    handle_design(prefix, True)

