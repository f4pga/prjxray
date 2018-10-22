#!/usr/bin/env python3

import sys

from prjxray.segmaker import Segmaker

tags = dict()
en_tags = dict()

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
            if "HCLK_CK_BUFH" in src:
                en_tag = "ENABLE_BUFFER.%s" % src
                en_tags[en_tag] = src

for arg in sys.argv[1:]:
    print("Processing %s." % arg)
    segmk = Segmaker(arg + ".bits")

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
            segmk.add_tile_tag(tile, tag, 1)
            if "HCLK_CK_BUFH" in src:
                en_tag = "ENABLE_BUFFER.%s" % src
                segmk.add_tile_tag(tile, en_tag, 1)
            for tag, tag_dst in tags.items():
                if tag_dst != dst:
                    segmk.add_tile_tag(tile, tag, 0)
            for en_tag, en_tag_src in en_tags.items():
                if en_tag_src != src:
                    segmk.add_tile_tag(tile, en_tag, 0)

    segmk.compile()
    segmk.write(arg)
