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

from prjxray.segmaker import Segmaker, add_site_group_zero

INT = "INT"
BIN = "BIN"
BOOL = "BOOL"
STR = "STR"


def bitfilter_gtx_channel_x(frame, bit):
    # Filter out interconnect bits.
    if frame not in [28, 29, 30, 31]:
       return False

    return True


def bitfilter_gtx_channel_x_mid(frame, bit):
    # Filter out interconnect bits.
    if frame not in [0, 1, 2, 3]:
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
        primitives_list = json.load(f)

    for primitive in primitives_list:
        tile_type = primitive["tile_type"]
        params_list = primitive["params"]

        for params in params_list:
            site = params["site"]

            if "GTXE2_CHANNEL" not in site:
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
                        param_encoding = param_encodings[param_values.index(
                            value)]
                        bitstr = [
                            int(x) for x in "{value:0{digits}b}".format(
                                value=param_encoding, digits=param_digits)
                            [::-1]
                        ]

                        for i in range(param_digits):
                            segmk.add_site_tag(
                                site, '%s[%u]' % (param, i), bitstr[i])
                    elif param_type == BIN:
                        bitstr = [
                            int(x) for x in "{value:0{digits}b}".format(
                                value=value, digits=param_digits)[::-1]
                        ]

                        for i in range(param_digits):
                            segmk.add_site_tag(
                                site, "%s[%u]" % (param, i), bitstr[i])
                    elif param_type == BOOL:
                        segmk.add_site_tag(site, param, value == "TRUE")
                    else:
                        assert param_type == STR

                        # The RXSLIDE_MODE parameter has overlapping bits
                        # for its possible values. We need to treat it
                        # differently
                        if param == "RXSLIDE_MODE":
                            add_site_group_zero(
                                segmk, site, "{}.".format(param), param_values,
                                "OFF", value)
                        else:
                            for param_value in param_values:
                                segmk.add_site_tag(
                                    site, "{}.{}".format(param, param_value),
                                    value == param_value)

                for param in ["TXUSRCLK", "TXUSRCLK2", "TXPHDLYTSTCLK",
                              "RXUSRCLK", "RXUSRCLK2", "DRPCLK"]:
                    segmk.add_site_tag(site, "INV_" + param, params[param])

    gtx_channel_x = [
        "GTX_CHANNEL_0",
        "GTX_CHANNEL_1",
        "GTX_CHANNEL_2",
        "GTX_CHANNEL_3",
    ]

    gtx_channel_x_mid = [
        "GTX_CHANNEL_0_MID_LEFT",
        "GTX_CHANNEL_1_MID_LEFT",
        "GTX_CHANNEL_2_MID_LEFT",
        "GTX_CHANNEL_3_MID_LEFT",
        "GTX_CHANNEL_0_MID_RIGHT",
        "GTX_CHANNEL_1_MID_RIGHT",
        "GTX_CHANNEL_2_MID_RIGHT",
        "GTX_CHANNEL_3_MID_RIGHT",
    ]

    if tile_type in gtx_channel_x:
        bitfilter = bitfilter_gtx_channel_x
    elif tile_type in gtx_channel_x_mid:
        bitfilter = bitfilter_gtx_channel_x_mid
    else:
        assert False, tile_type

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
