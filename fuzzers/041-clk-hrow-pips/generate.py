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
import os.path
import re
from prjxray.segmaker import Segmaker


def src_has_active_bit(src):
    if re.match(r"^CLK_HROW_CK_INT_[01]_[01]", src) is not None:
        return False
    return True


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    clk_list = {}
    casco_list = {}
    ignpip = set()

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'clk_hrow', 'clk_hrow_bot_r.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []
                clk_list[tile_type] = set()
                casco_list[tile_type] = set()

            pipdata[tile_type].append((src, dst))

            if 'CASCO' in dst:
                casco_list[tile_type].add(dst)

            if dst.startswith('CLK_HROW_CK_MUX_OUT_'):
                clk_list[tile_type].add(src)

            if dst.startswith('CLK_HROW_BOT_R_CK_BUFG_'):
                if 'CASCIN' not in src:
                    clk_list[tile_type].add(src)

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'clk_hrow', 'clk_hrow_top_r.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []
                clk_list[tile_type] = set()
                casco_list[tile_type] = set()

            pipdata[tile_type].append((src, dst))

            if 'CASCO' in dst:
                casco_list[tile_type].add(dst)

            if dst.startswith('CLK_HROW_CK_MUX_OUT_'):
                clk_list[tile_type].add(src)

            if dst.startswith('CLK_HROW_TOP_R_CK_BUFG_'):
                if 'CASCIN' not in src:
                    clk_list[tile_type].add(src)

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('CLK_HROW'):
                continue

            pip_prefix, _ = pip.split(".")
            tile_from_pip, tile_type = pip_prefix.split('/')
            assert tile == tile_from_pip
            _, src = src.split("/")
            _, dst = dst.split("/")
            pnum = int(pnum)
            pdir = int(pdir)

            if tile not in tiledata:
                tiledata[tile] = {
                    "type": tile_type,
                    "pips": set(),
                    "srcs": set(),
                    "dsts": set()
                }

            tiledata[tile]["pips"].add((src, dst))
            tiledata[tile]["srcs"].add(src)
            tiledata[tile]["dsts"].add(dst)

            if pdir == 0:
                tiledata[tile]["srcs"].add(dst)
                tiledata[tile]["dsts"].add(src)

            if pnum == 1 or pdir == 0:
                ignpip.add((src, dst))

    active_gclks = {}
    active_clks = {}

    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]
        pips = pips_srcs_dsts["pips"]

        if tile not in active_clks:
            active_clks[tile] = set()

        for src, dst in pips_srcs_dsts["pips"]:
            active_clks[tile].add(src)

            if 'GCLK' in src:
                if src not in active_gclks:
                    active_gclks[src] = set()

                active_gclks[src].add(tile)

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            elif (src, dst) in pips:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif dst not in tiledata[tile]["dsts"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

    for tile_type, srcs in clk_list.items():
        for tile, pips_srcs_dsts in tiledata.items():
            for src in srcs:
                #Don't solve fake features
                if not src_has_active_bit(src):
                    continue
                if 'GCLK' not in src:
                    active = src in active_clks[tile]
                    segmk.add_tile_tag(tile, '{}_ACTIVE'.format(src), active)
                else:
                    if src not in active_gclks:
                        segmk.add_tile_tag(tile, '{}_ACTIVE'.format(src), 0)
                    elif tile in active_gclks[src]:
                        segmk.add_tile_tag(tile, '{}_ACTIVE'.format(src), 1)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
