#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import os
import os.path


def bitfilter(frame, word):
    if frame <= 1:
        return False

    return True


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    ignpip = set()

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'cmt_top', 'cmt_top_l_upper_t.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []

            pipdata[tile_type].append((src, dst))

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'cmt_top', 'cmt_top_r_upper_t.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []

            pipdata[tile_type].append((src, dst))

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('CMT_TOP'):
                continue

            if 'UPPER_B' in tile:
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
                    "dsts": set(),
                }

            tiledata[tile]["pips"].add((src, dst))
            tiledata[tile]["srcs"].add(src)
            tiledata[tile]["dsts"].add(dst)

            if pdir == 0:
                tiledata[tile]["srcs"].add(dst)
                tiledata[tile]["dsts"].add(src)

            if dst.startswith('CMT_TOP_R_UPPER_T_CLK') or \
               dst.startswith('CMT_TOP_L_UPPER_T_CLK'):
                ignpip.add((src, dst))

    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]
        pips = pips_srcs_dsts["pips"]

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            elif (src, dst) in pips:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif (src, dst) not in tiledata[tile]["pips"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

        internal_feedback = False
        for src, dst in [
            ('CMT_TOP_L_CLKFBOUT2IN', 'CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN'),
            ('CMT_TOP_R_CLKFBOUT2IN', 'CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN'),
        ]:
            if (src, dst) in pips:
                internal_feedback = True

        segmk.add_tile_tag(tile, "EXTERNAL_FEEDBACK", not internal_feedback)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
