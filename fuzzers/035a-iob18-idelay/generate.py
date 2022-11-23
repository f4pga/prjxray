#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022  The Project X-Ray Authors.
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
    if frame < 26:
        return False

    return True


def main():
    segmk = Segmaker("design.bits", verbose=True)

    # Load tags
    with open("params.json", "r") as fp:
        data = json.load(fp)

    idelay_types = ["FIXED", "VARIABLE", "VAR_LOAD"]
    delay_srcs = ["IDATAIN", "DATAIN"]

    # Output tags
    for params in data:
        segmk.add_site_tag(params['IDELAY_IN_USE'], 'IN_USE', True)
        segmk.add_site_tag(params['IDELAY_NOT_IN_USE'], 'IN_USE', False)

        loc = verilog.unquote(params["LOC"])

        # Delay type
        value = verilog.unquote(params["IDELAY_TYPE"])
        value = value.replace(
            "_PIPE", "")  # VAR_LOAD and VAR_LOAD_PIPE are the same
        add_site_group_zero(
            segmk, loc, "IDELAY_TYPE_", idelay_types, "FIXED", value)

        # Delay value
        value = int(params["IDELAY_VALUE"])
        for i in range(5):
            segmk.add_site_tag(
                loc, "IDELAY_VALUE[%01d]" % i, ((value >> i) & 1) != 0)
            segmk.add_site_tag(
                loc, "ZIDELAY_VALUE[%01d]" % i, ((value >> i) & 1) == 0)

        # Delay source
        value = verilog.unquote(params["DELAY_SRC"])
        for x in delay_srcs:
            segmk.add_site_tag(loc, "DELAY_SRC_%s" % x, int(value == x))

        value = verilog.unquote(params["CINVCTRL_SEL"])
        segmk.add_site_tag(loc, "CINVCTRL_SEL", int(value == "TRUE"))

        value = verilog.unquote(params["PIPE_SEL"])
        segmk.add_site_tag(loc, "PIPE_SEL", int(value == "TRUE"))

        if "IS_C_INVERTED" in params:
            segmk.add_site_tag(
                loc, "IS_C_INVERTED", int(params["IS_C_INVERTED"]))
            segmk.add_site_tag(loc, "ZINV_C", 1 ^ int(params["IS_C_INVERTED"]))

        segmk.add_site_tag(
            loc, "IS_DATAIN_INVERTED", int(params["IS_DATAIN_INVERTED"]))
        if params['IBUF_IN_USE']:
            value = verilog.unquote(params["HIGH_PERFORMANCE_MODE"])
            segmk.add_site_tag(
                loc, "HIGH_PERFORMANCE_MODE", int(value == "TRUE"))

            segmk.add_site_tag(
                loc, "IS_IDATAIN_INVERTED", int(params["IS_IDATAIN_INVERTED"]))

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
