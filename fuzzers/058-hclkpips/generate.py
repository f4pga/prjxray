#!/usr/bin/env python3

import sys, os, re

sys.path.append("../../../utils/")
from segmaker import segmaker

tags = dict()

print("Preload all tags.")
for arg in sys.argv[1:]:
    with open(arg + ".txt", "r") as f:
        for line in f:
            tile, pip = line.split()
            _, pip = pip.split("/")
            tile_type, pip = pip.split(".")
            src, dst = pip.split("->>")
            tag = "%s.%s" % (dst, src)
            tags[tag] = dst

for arg in sys.argv[1:]:
    print("Processing %s." % arg)
    segmk = segmaker(arg + ".bits")

    tiledata = dict()
    pipdata = dict()
    ignpip = set()

    with open(arg + ".txt", "r") as f:
        for line in f:
            tile, pip = line.split()
            _, pip = pip.split("/")
            tile_type, pip = pip.split(".")
            src, dst = pip.split("->>")
            tag = "%s.%s" % (dst, src)
            segmk.addtag(tile, tag, 1)
            for tag, tag_dst in tags.items():
                if tag_dst != dst:
                    segmk.addtag(tile, tag, 0)

    segmk.compile()
    segmk.write(arg)

