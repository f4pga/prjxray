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

import os, sys, json

from prjxray.util import OpenSafeFile

def main(argv):
    if len(argv) != 3:
        print("Usage example: python3 %s HCLK_R HCLK_SW6E3" % sys.argv[0])
        sys.exit(1)

    with OpenSafeFile("%s/%s/tileconn.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        tileconn = json.load(f)

    outdata = list()
    max_tiletype_len = 1

    for entry in tileconn:
        if entry["tile_types"][0] == sys.argv[1]:
            this_idx, other_idx = 0, 1
            delta_x, delta_y = entry["grid_deltas"]
        elif entry["tile_types"][1] == sys.argv[1]:
            this_idx, other_idx = 1, 0
            delta_x, delta_y = -entry["grid_deltas"][0], -entry["grid_deltas"][
                1]
        else:
            continue

        for wire_pair in entry["wire_pairs"]:
            if wire_pair[this_idx] != sys.argv[2]:
                continue

            outdata.append(
                (
                    delta_x, delta_y, entry["tile_types"][other_idx],
                    wire_pair[other_idx]))
            max_tiletype_len = max(
                max_tiletype_len, len(entry["tile_types"][other_idx]))

    for entry in outdata:
        print(
            "%3d %3d  %-*s  %s" %
            (entry[0], entry[1], max_tiletype_len, entry[2], entry[3]))


if __name__ == "__main__":
    main(sys.argv)
