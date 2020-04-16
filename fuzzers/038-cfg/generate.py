#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog
from prjxray import segmaker


def bitfilter(frame, word):
    if frame < 26:
        return False
    return True


def run():

    segmk = Segmaker("design.bits")

    print("Loading tags")
    f = open('params.jl', 'r')
    design = json.load(f)
    for p in design:
        ps = p["params"]
        if p["site_type"] in "ICAP":
            param = verilog.unquote(ps["ICAP_WIDTH"])
            segmaker.add_site_group_zero(
                segmk, p["site"], "ICAP_WIDTH_", ["X32", "X8", "X16"], "X32",
                param)
        elif p["site_type"] in "BSCAN":
            param = str(ps["JTAG_CHAIN"])
            segmaker.add_site_group_zero(
                segmk, p["site"], "JTAG_CHAIN_", ["1", "2", "3", "4"], param,
                param)
        elif p["site_type"] in "CAPTURE":
            param = verilog.unquote(ps["ONESHOT"])
            segmk.add_site_tag(
                p["site"], "ONESHOT", True if param in "TRUE" else False)
        elif p["site_type"] in "STARTUP":
            param = verilog.unquote(ps["PROG_USR"])
            segmk.add_site_tag(
                p["site"], "PROG_USR", True if param in "TRUE" else False)
        elif p["site_type"] in "FRAME_ECC":
            param = verilog.unquote(ps["FARSRC"])
            segmaker.add_site_group_zero(
                segmk, p["site"], "FARSRC_", ["FAR", "EFAR"], param, param)
        elif p["site_type"] in ["USR_ACCESS", "DCIRESET"]:
            feature = "ENABLED"
            segmk.add_site_tag(
                p["site"], feature, True if ps["ENABLED"] else False)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


run()
