#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from prjxray.segmaker import Segmaker
import os, re
import os.path


def bitfilter(frame, word):
    if frame < 28:
        return False
    return True


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    ignpip = set()

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'ioi', 'rioi.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []

            pipdata[tile_type].append((src, dst))

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()
            if not tile.startswith('RIOI') or "X43Y9" in tile:
                continue

            log = open("log.txt", "a")
            print(line, file=log)
            pip_prefix, _ = pip.split(".")
            tile_from_pip, tile_type = pip_prefix.split('/')

            _, src = src.split("/")
            _, dst = dst.split("/")
            pnum = int(pnum)
            pdir = int(pdir)

            if tile not in tiledata:
                tiledata[tile] = {
                    "type": tile_type,
                    "pips": set(),
                    "srcs": set(),
                    "dsts": set(),
                }

            tiledata[tile]["pips"].add((src, dst))
            tiledata[tile]["srcs"].add(src)
            tiledata[tile]["dsts"].add(dst)

            if pdir == 0:
                tiledata[tile]["srcs"].add(dst)
                tiledata[tile]["dsts"].add(src)

    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]

        if tile_type.startswith('RIOI'):
            tile_type = 'RIOI'

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            if re.match(r'.*PHASER.*', src) or re.match(r'.*CLKDIV[PFB].*',
                                                        dst):
                pass
            elif (src, dst) in tiledata[tile]["pips"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif dst not in tiledata[tile]["dsts"]:
                disable_pip = True

                if dst == 'IOI_OCLKM_0' and 'IOI_OCLK_0' in tiledata[tile][
                        "dsts"]:
                    disable_pip = False

                if dst == 'IOI_OCLKM_1' and 'IOI_OCLK_1' in tiledata[tile][
                        "dsts"]:
                    disable_pip = False

                if disable_pip:
                    segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
