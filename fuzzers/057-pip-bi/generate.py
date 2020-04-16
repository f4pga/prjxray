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

import os

from prjxray.segmaker import Segmaker

segmk = Segmaker("design.bits")

tiledata = dict()
pipdata = set()

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        ab, dst, src = line.split()
        tile, dst = dst.split("/")
        _, src = src.split("/")

        if tile not in tiledata:
            tiledata[tile] = {
                "pips": set(),
                "nodes": set(),
            }

        if ab == "A":
            tiledata[tile]["pips"].add((dst, src))
            pipdata.add((dst, src))
        else:
            tiledata[tile]["nodes"].add(src)
            tiledata[tile]["nodes"].add(dst)

for tile, pips_nodes in tiledata.items():
    pips = pips_nodes["pips"]
    nodes = pips_nodes["nodes"]

    for dst, src in pipdata:
        if (dst, src) in pips:
            segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
        elif dst not in nodes and src not in nodes:
            segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)


def bitfilter(frame_idx, bit_idx):
    return frame_idx in [0, 1]


segmk.compile(bitfilter=bitfilter)
segmk.write(allow_empty=True)
