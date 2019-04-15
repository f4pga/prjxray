#!/usr/bin/env python3

import os
import os.path
from prjxray.segmaker import Segmaker


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

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('CLK_HROW'):
                continue

            if not dst.startswith('CLK_HROW_CK_MUX_OUT_'):
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

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            elif (src, dst) in pips:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif dst not in tiledata[tile]["dsts"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
