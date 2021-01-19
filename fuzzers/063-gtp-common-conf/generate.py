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


def bitfilter_gtp_common_mid(frame, bit):
    # Filter out interconnect bits.
    if frame not in [0, 1]:
        return False

    return True


def bitfilter_gtp_common(frame, bit):
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
        params_dict = json.load(f)
        tile_type = params_dict["tile_type"]
        params_list = params_dict["params"]

    for params in params_list:
        site = params["site"]

        if "GTPE2_COMMON" not in site:
            continue

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
                        segmk.add_site_tag(
                            site, '%s[%u]' % (param, i), bitstr[i])
                else:
                    assert param_type == BIN
                    bitstr = [
                        int(x) for x in "{value:0{digits}b}".format(
                            value=value, digits=param_digits)[::-1]
                    ]

                    for i in range(param_digits):
                        segmk.add_site_tag(
                            site, "%s[%u]" % (param, i), bitstr[i])

            for param, invert in [("GTGREFCLK1", 0), ("GTGREFCLK0", 0),
                                  ("PLL0LOCKDETCLK", 1), ("PLL1LOCKDETCLK",
                                                          1), ("DRPCLK", 1)]:
                if invert:
                    segmk.add_site_tag(
                        site, "ZINV_" + param, 1 ^ params[param])
                else:
                    segmk.add_site_tag(site, "INV_" + param, params[param])

    for params in params_list:
        site = params["site"]

        if "IBUFDS_GTE2" not in site:
            continue

        in_use = params["IN_USE"]
        segmk.add_site_tag(site, "IN_USE", in_use)

        if in_use:
            tile = params["tile"]

            for param in ["CLKRCV_TRST", "CLKCM_CFG"]:
                value = params[param]
                segmk.add_site_tag(site, param, "TRUE" in value)

            bitstr = [
                int(x) for x in "{value:0{digits}b}".format(
                    value=params["CLKSWING_CFG"], digits=2)[::-1]
            ]

            for i in range(2):
                segmk.add_tile_tag(
                    tile, "IBUFDS_GTE2.%s[%u]" % (param, i), bitstr[i])

    if tile_type == "GTP_COMMON":
        bitfilter = bitfilter_gtp_common
    elif tile_type == "GTP_COMMON_MID_RIGHT":
        bitfilter = bitfilter_gtp_common_mid
    else:
        assert False, tile_type

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
