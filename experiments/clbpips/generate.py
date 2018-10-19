#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import util

segmk = Segmaker(util.get_db_root(), "design.bits")

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        line, active = line.split()
        tile, pip = line.split("/")
        _, pip = pip.split(".")

        print(tile, pip, active)
        segmk.addtag(tile, pip, int(active))

segmk.compile()
segmk.write()
