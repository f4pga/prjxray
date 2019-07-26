#!/usr/bin/env python3
import json

from prjxray.segmaker import Segmaker, add_site_group_zero
from prjxray import util
from prjxray import verilog

segmk = Segmaker("design.bits", verbose=True)

# Load tags
with open("params.json", "r") as fp:
    data = json.load(fp)

# Output tags
for params in data:
    loc = params["LOC"]

    segmk.add_site_tag(loc, "IN_USE", params["IN_USE"])


def bitfilter(frame, word):
    if frame < 32 or frame > 33:
        return False

    return True


segmk.compile(bitfilter=bitfilter)
segmk.write()
