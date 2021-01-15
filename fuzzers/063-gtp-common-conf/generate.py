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
import os
from enum import Enum

from prjxray.segmaker import Segmaker

INT = "INT"
BIN = "BIN"


def bitfilter(frame, bit):
    # Filter out interconnect bits.
    if frame not in [28, 29]:
        return False

    return True


def main():
    segmk = Segmaker("design.bits")

    fuz_dir = os.getenv("FUZDIR", None)
    assert fuz_dir
    with open(os.path.join(fuz_dir, "attrs.json"), "r") as attr_file:
        attrs = json.load(attr_file)

    print("Loading tags")
    with open("params.json") as f:
        params = json.load(f)

    site = params["site"]
    in_use = params["IN_USE"]

    segmk.add_site_tag(site, "IN_USE", in_use)

    if in_use:
        for param, param_info in attrs.items():
            value = params[param]
            param_type = param_info["type"]
            param_digits = param_info["digits"]
            param_values = param_info["values"]

            if param_type == INT:
                param_encodings = param_info["encoding"]
                param_encoding = param_encodings[param_values.index(value)]
                bitstr = [
                    int(x) for x in "{value:0{digits}b}".format(
                        value=param_encoding, digits=param_digits)[::-1]
                ]

                for i in range(param_digits):
                    segmk.add_site_tag(site, '%s[%u]' % (param, i), bitstr[i])
            else:
                assert param_type == BIN
                bitstr = [
                    int(x) for x in "{value:0{digits}b}".format(
                        value=value, digits=param_digits)[::-1]
                ]

                for i in range(param_digits):
                    segmk.add_site_tag(site, "%s[%u]" % (param, i), bitstr[i])

        for param, invert in [("GTGREFCLK1", 0), ("GTGREFCLK0", 0),
                              ("PLL0LOCKDETCLK", 1), ("PLL1LOCKDETCLK",
                                                      1), ("DRPCLK", 1)]:
            if invert:
                segmk.add_site_tag(site, "ZINV_" + param, 1 ^ params[param])
            else:
                segmk.add_site_tag(site, "INV_" + param, params[param])

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
