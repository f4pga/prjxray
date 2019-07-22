#!/usr/bin/env python3
import json

from prjxray.segmaker import Segmaker
from prjxray import util
from prjxray import verilog

segmk = Segmaker("design.bits", verbose=True)

# Load tags
with open("params.json", "r") as fp:
    data = json.load(fp)

idelay_types = ["FIXED", "VARIABLE", "VAR_LOAD"]
delay_srcs = ["IDATAIN", "DATAIN"]

# Output tags
for params in data:
    loc = verilog.unquote(params["LOC"])

    # Delay type
    value = verilog.unquote(params["IDELAY_TYPE"])
    value = value.replace(
        "_PIPE", "")  # VAR_LOAD and VAR_LOAD_PIPE are the same
    for x in idelay_types:
        segmk.add_site_tag(loc, "IDELAY_TYPE_%s" % x, int(value == x))

    # Delay value
    value = int(params["IDELAY_VALUE"])
    for i in range(5):
        segmk.add_site_tag(
            loc, "IDELAY_VALUE[%01d]" % i, ((value >> i) & 1) != 0)

    # Delay source
    value = verilog.unquote(params["DELAY_SRC"])
    for x in delay_srcs:
        segmk.add_site_tag(loc, "DELAY_SRC_%s" % x, int(value == x))

    value = verilog.unquote(params["HIGH_PERFORMANCE_MODE"])
    segmk.add_site_tag(loc, "HIGH_PERFORMANCE_MODE", int(value == "TRUE"))

    value = verilog.unquote(params["CINVCTRL_SEL"])
    segmk.add_site_tag(loc, "CINVCTRL_SEL", int(value == "TRUE"))

    value = verilog.unquote(params["PIPE_SEL"])
    segmk.add_site_tag(loc, "PIPE_SEL", int(value == "TRUE"))

    if "IS_C_INVERTED" in params:
        segmk.add_site_tag(loc, "IS_C_INVERTED", int(params["IS_C_INVERTED"]))

    segmk.add_site_tag(
        loc, "IS_DATAIN_INVERTED", int(params["IS_DATAIN_INVERTED"]))
    segmk.add_site_tag(
        loc, "IS_IDATAIN_INVERTED", int(params["IS_IDATAIN_INVERTED"]))


def bitfilter(frame_idx, bit_idx):
    return True


segmk.compile(bitfilter=bitfilter)
segmk.write()
