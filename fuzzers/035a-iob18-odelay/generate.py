#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2023  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import json

from prjxray.segmaker import Segmaker, add_site_group_zero
from prjxray import verilog


def bitfilter(frame, word):
    return frame >= 27

def main():
    segmk = Segmaker("design.bits", verbose=True)

    # Load tags
    with open("params.json", "r") as fp:
        data = json.load(fp)

    odelay_types = ["FIXED", "VARIABLE", "VAR_LOAD"]
    delay_srcs = ["ODATAIN"]

    # Output tags
    for params in data:
        if params['ODELAY_BYPASS']:
            prims = params['ODELAY_NOT_IN_USE'].split(" ")
            segmk.add_site_tag(prims[0], 'IN_USE', False)
            segmk.add_site_tag(prims[1], 'IN_USE', False)
            continue
        segmk.add_site_tag(params['ODELAY_IN_USE'], 'IN_USE', True)
        segmk.add_site_tag(params['ODELAY_NOT_IN_USE'], 'IN_USE', False)

        loc = verilog.unquote(params["LOC"])

        # Delay type
		# VAR_LOAD and VAR_LOAD_PIPE are the same
        value = verilog.unquote(params["ODELAY_TYPE"])
        add_site_group_zero(
            segmk, loc, "ODELAY_TYPE_", odelay_types, "FIXED", value)

        # Delay value
        value = int(params["ODELAY_VALUE"])
        for i in range(5):
            segmk.add_site_tag(
                loc, "ODELAY_VALUE[%01d]" % i, ((value >> i) & 1) != 0)
            segmk.add_site_tag(
                loc, "ZODELAY_VALUE[%01d]" % i, ((value >> i) & 1) == 0)

        value = verilog.unquote(params["CINVCTRL_SEL"])
        segmk.add_site_tag(loc, "CINVCTRL_SEL", int(value == "TRUE"))

        value = verilog.unquote(params["PIPE_SEL"])
        segmk.add_site_tag(loc, "PIPE_SEL", int(value == "TRUE"))

        if "IS_C_INVERTED" in params and verilog.unquote(params["CINVCTRL_SEL"]) != "TRUE":
            segmk.add_site_tag(
                loc, "IS_C_INVERTED", int(params["IS_C_INVERTED"]))
            segmk.add_site_tag(loc, "ZINV_C", 1 ^ int(params["IS_C_INVERTED"]))

        value = verilog.unquote(params["HIGH_PERFORMANCE_MODE"])
        segmk.add_site_tag(
            loc, "HIGH_PERFORMANCE_MODE", int(value == "TRUE"))

        segmk.add_site_tag(
            loc, "ZINV_ODATAIN", 1 ^ int(params["IS_ODATAIN_INVERTED"]))

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
