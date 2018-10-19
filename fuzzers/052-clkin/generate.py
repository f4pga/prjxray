#!/usr/bin/env python3

import os, re

from prjxray.segmaker import Segmaker
from prjxray import util

segmk = Segmaker(util.get_db_root(), "design.bits")

tiledata = dict()
pipdata = dict()
ignpip = set()

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        tile, pip, src, dst, pnum, pdir = line.split()
        _, pip = pip.split(".")
        _, src = src.split("/")
        _, dst = dst.split("/")
        pnum = int(pnum)
        pdir = int(pdir)

        if tile not in tiledata:
            tiledata[tile] = {"pips": set(), "srcs": set(), "dsts": set()}

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

        if pnum == 1 or pdir == 0 or not re.match(r"^CLK", dst):
            ignpip.add(pip)

for tile, pips_srcs_dsts in tiledata.items():
    pips = pips_srcs_dsts["pips"]
    srcs = pips_srcs_dsts["srcs"]
    dsts = pips_srcs_dsts["dsts"]

    for pip, src_dst in pipdata.items():
        src, dst = src_dst
        if pip in ignpip:
            pass
        elif pip in pips:
            segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
        elif src_dst[1] not in dsts:
            segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)


def bitfilter(frame_idx, bit_idx):
    assert os.getenv("XRAY_DATABASE") in ["artix7", "kintex7"]
    if frame_idx == 0 and bit_idx == 48:
        return False
    if frame_idx == 1 and bit_idx == 31:
        return False
    return frame_idx in [0, 1]


segmk.compile(bitfilter=bitfilter)
segmk.write()
