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

import sys
import re

from prjxray.segmaker import Segmaker

tags = dict()
en_tags = dict()

print("Preload all tags.")
for arg in sys.argv[1:]:
    with open(arg + ".txt", "r") as f:
        for line in f:
            tile, pip = line.split()
            _, pip = pip.split("/")
            tile_type, pip = pip.split(".")
            src, dst = pip.split("->>")
            tag = "%s.%s" % (dst, src)
            tags[tag] = dst
            if "HCLK_CK_BUFH" in src:
                en_tag = "ENABLE_BUFFER.%s" % src
                en_tags[en_tag] = src

for arg in sys.argv[1:]:
    print("Processing %s." % arg)
    segmk = Segmaker(arg + ".bits")

    tiledata = dict()
    pipdata = dict()
    ignpip = set()

    with open(arg + ".txt", "r") as f:
        for line in f:
            tile, pip = line.split()
            _, pip = pip.split("/")
            tile_type, pip = pip.split(".")
            src, dst = pip.split("->>")

            # FIXME: workaround for https://github.com/SymbiFlow/prjxray/issues/392
            if "CLB_IO_CLK" not in segmk.grid[tile]["bits"]:
                print("WARNING: dropping tile %s" % tile)
                continue
            tag = "%s.%s" % (dst, src)

            def add_tile_tag(tag, val):
                # Workaround for https://github.com/SymbiFlow/prjxray/issues/396
                # TODO: drop from tcl or make an ignpip
                if re.match(r"HCLK_CK_INOUT_.*", tag):
                    # print("Dropping %s %s" % (tag, val))
                    return
                segmk.add_tile_tag(tile, tag, val)

            add_tile_tag(tag, 1)
            if "HCLK_CK_BUFH" in src:
                en_tag = "ENABLE_BUFFER.%s" % src
                add_tile_tag(en_tag, 1)
            for tag, tag_dst in tags.items():
                if tag_dst != dst:
                    add_tile_tag(tag, 0)
            for en_tag, en_tag_src in en_tags.items():
                if en_tag_src != src:
                    add_tile_tag(en_tag, 0)

    segmk.compile()
    segmk.write(arg)
