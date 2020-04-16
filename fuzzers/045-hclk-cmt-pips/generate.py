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

from prjxray.segmaker import Segmaker
import os
import os.path


def bitfilter(frame, word):
    if frame < 26:
        return False

    return True


IOCLK_MAP = {
    'HCLK_IOI_I2IOCLK_TOP0': 'HCLK_CMT_CCIO0',
    'HCLK_IOI_I2IOCLK_TOP1': 'HCLK_CMT_CCIO1',
    'HCLK_IOI_I2IOCLK_BOT0': 'HCLK_CMT_CCIO2',
    'HCLK_IOI_I2IOCLK_BOT1': 'HCLK_CMT_CCIO3',
}

IOCLK_SRCS = set(IOCLK_MAP.values())


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    ignpip = set()
    tile_ports = {}

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'hclk_cmt', 'hclk_cmt.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []
                tile_ports[tile_type] = set()

            pipdata[tile_type].append((src, dst))
            tile_ports[tile_type].add(src)
            tile_ports[tile_type].add(dst)

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'hclk_cmt', 'hclk_cmt_l.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []
                tile_ports[tile_type] = set()

            pipdata[tile_type].append((src, dst))
            tile_ports[tile_type].add(src)
            tile_ports[tile_type].add(dst)

    tile_to_cmt = {}
    cmt_to_hclk_cmt = {}
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt, tile = l.strip().split(',')

            tile_to_cmt[tile] = cmt

            if tile.startswith('HCLK_CMT'):
                cmt_to_hclk_cmt[cmt] = tile

    active_ioclks = set()

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            pip_prefix, _ = pip.split(".")
            tile_from_pip, tile_type = pip_prefix.split('/')
            assert tile == tile_from_pip
            _, src = src.split("/")
            _, dst = dst.split("/")
            pnum = int(pnum)
            pdir = int(pdir)

            if src in IOCLK_MAP:
                active_ioclks.add(
                    (cmt_to_hclk_cmt[tile_to_cmt[tile]], IOCLK_MAP[src]))

            if not tile.startswith('HCLK_CMT'):
                continue

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

    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]
        pips = pips_srcs_dsts["pips"]

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            elif (src, dst) in pips:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif dst not in tiledata[tile]["dsts"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

        for port in tile_ports[tile_type]:

            # These ones do not have any outgoing connections from the tile.
            if "FREQ_REF" in port:
                continue

            # There seems to be no special bits related to use of
            # HCLK_CMT_MUX_CLKINT_n wires.
            if "HCLK_CMT_MUX_CLKINT" in port:
                continue

            # It seems that CCIOn_USED is not enabled when a net goes through
            # FREQ_REFn. Do not emit this tag if this happens.
            if "CCIO" in port:
                n = int(port[-1])
                dst = "HCLK_CMT_MUX_OUT_FREQ_REF{}".format(n)
                if dst in tiledata[tile]["dsts"]:
                    continue

            if port in tiledata[tile]["dsts"] or port in tiledata[tile]["srcs"]:
                segmk.add_tile_tag(tile, "{}_USED".format(port), 1)
            else:
                segmk.add_tile_tag(tile, "{}_USED".format(port), 0)

        for ioclk in IOCLK_SRCS:
            if ioclk in tiledata[tile]["srcs"] or (tile,
                                                   ioclk) in active_ioclks:
                segmk.add_tile_tag(tile, "{}_ACTIVE".format(ioclk), 1)
            else:
                segmk.add_tile_tag(tile, "{}_ACTIVE".format(ioclk), 0)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
