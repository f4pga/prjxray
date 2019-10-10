#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import os
import os.path
import itertools
import random

def bitfilter(frame, word):
    if frame <= 1:
        return False

    return True


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    ppipdata = {}
    ignpip = set()

    # Load PIP lists
    piplists = ['cmt_top_l_upper_t.txt', 'cmt_top_r_upper_t.txt']
    for piplist in piplists:
        with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                               'cmt_top', piplist)) as f:
            for l in f:
                tile_type, dst, src = l.strip().split('.')
                if tile_type not in pipdata:
                    pipdata[tile_type] = []

                pipdata[tile_type].append((src, dst))

    # Load PPIP lists (to exclude them)
    ppiplists = ['ppips_cmt_top_l_upper_t.db', 'ppips_cmt_top_r_upper_t.db']
    for ppiplist in ppiplists:
        fname = os.path.join(
            os.getenv('FUZDIR'), '..', '071-ppips', 'build', ppiplist)
        with open(fname, 'r') as f:
            for l in f:
                pip_data, pip_type = l.strip().split()

                print(pip_data, pip_type)
                if pip_type != 'always':
                    continue

                tile_type, dst, src = pip_data.split('.')
                if tile_type not in ppipdata:
                    ppipdata[tile_type] = []

                ppipdata[tile_type].append((src, dst))

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('CMT_TOP'):
                continue

            if 'UPPER_B' in tile:
                continue
            if 'LOWER_T' in tile:
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

            # Ignore pseudo pips
            for ppip in ppipdata[tile_type]:
                if ppip == (src, dst):
                    ignpip.add((
                        src,
                        dst,
                    ))

    tags = {}
    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]
        pips = pips_srcs_dsts["pips"]

        if tile not in tags:
            tags[tile] = {}

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            elif (src, dst) in pips:
                tags[tile]["%s.%s" % (dst, src)] = 1
            elif (src, dst) not in tiledata[tile]["pips"]:
                tags[tile]["%s.%s" % (dst, src)] = 0

        internal_feedback = False
        for src, dst in [
            ('CMT_TOP_L_CLKFBOUT2IN', 'CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN'),
            ('CMT_TOP_R_CLKFBOUT2IN', 'CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN'),
        ]:
            if (src, dst) in pips:
                internal_feedback = True

        tags[tile]["EXTERNAL_FEEDBACK"] = int(not internal_feedback)


    # Those tags are exclusive. This is due to the fact that Vivado sometimes
    # report routes that does not correspond to underlying bit configuration.
    xored_tags = [
        ("CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN.CMT_TOP_L_UPPER_T_CLKFBIN",
         "CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN.CMT_TOP_L_UPPER_T_PLLE2_CLK_FB_INT"),
        ("CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN.CMT_TOP_R_UPPER_T_CLKFBIN",
         "CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN.CMT_TOP_R_UPPER_T_PLLE2_CLK_FB_INT"),
    ]

    for tile in tags.keys():
        for pair in xored_tags:
            for tag_a, tag_b in itertools.permutations(pair, 2):

                if tag_a in tags[tile] and tag_b in tags[tile]:
                    if tags[tile][tag_a] == tags[tile][tag_b]:
                        d = tags[tile]
                        del d[tag_a]
                        del d[tag_b]

    for tile, tile_tags in tags.items():
        for t, v in tile_tags.items():
            segmk.add_tile_tag(tile, t, v)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
