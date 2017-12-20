#!/usr/bin/env python3

import sys, os, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

tiledata = dict()
pipdata = set()

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        ab, dst, src = line.split()
        tile, dst = dst.split("/")
        _, src = src.split("/")

        if tile not in tiledata:
            tiledata[tile] = {
                "pips": set(),
                "nodes": set(),
            }

        if ab == "A":
            tiledata[tile]["pips"].add((dst, src))
            pipdata.add((dst, src))
        else:
            tiledata[tile]["nodes"].add(src)
            tiledata[tile]["nodes"].add(dst)

for tile, pips_nodes in tiledata.items():
    pips = pips_nodes["pips"]
    nodes = pips_nodes["nodes"]

    for dst, src in pipdata:
        if (dst, src) in pips:
            segmk.addtag(tile, "%s.%s" % (dst, src), 1)
        elif dst not in nodes and src not in nodes:
            segmk.addtag(tile, "%s.%s" % (dst, src), 0)

def bitfilter(frame_idx, bit_idx):
    assert os.getenv("XRAY_DATABASE") == "artix7"
    return frame_idx in [0, 1]

segmk.compile(bitfilter=bitfilter)
segmk.write()

