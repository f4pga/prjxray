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
    word = int(word / 32)

    # Clock-related PIPs in the GTP_COMMON_MID_[LEFT|RIGHT] have bits
    # from frame 0 to 7, hence, all the other frames are skipped.
    if frame not in [0, 1, 2, 3, 4, 5, 6, 7]:
        return False

    # All the Clock-related PIPs have bits at word 50 in the GTP_COMMON tile.
    # Filter out all bits not belonging to word 50.
    if word != 50:
        return False

    return True


def read_pip_data(pipfile, pipdata, tile_ports):
    part = os.getenv('XRAY_PART')
    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'gtp_common_mid_{}'.format(part), pipfile)) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []
                tile_ports[tile_type] = set()

            pipdata[tile_type].append((src, dst))
            tile_ports[tile_type].add(src)
            tile_ports[tile_type].add(dst)


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    ignpip = set()
    tile_ports = {}

    read_pip_data('gtp_common_mid_ck_mux.txt', pipdata, tile_ports)

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('GTP_COMMON_MID'):
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

            if "HCLK_GTP_CK_MUX" not in src:
                ignpip.add((src, dst))

    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]
        pips = pips_srcs_dsts["pips"]

        for src, dst in pipdata["GTP_COMMON"]:
            if (src, dst) in ignpip:
                pass
            elif (src, dst) in pips:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif src not in tiledata[tile]["srcs"] and dst not in tiledata[
                    tile]["dsts"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
