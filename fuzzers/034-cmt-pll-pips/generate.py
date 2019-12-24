#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import os
import os.path
import itertools


def bitfilter(frame, word):
    if frame < 28 or frame > 29:
        return False

    return True


def main():
    segmk = Segmaker("design.bits")

    designdata = {}
    tiledata = {}
    pipdata = {}
    ppipdata = {}
    ignpip = set()

    piplists = ['cmt_top_l_upper_t.txt', 'cmt_top_r_upper_t.txt']
    ppiplists = ['ppips_cmt_top_l_upper_t.db', 'ppips_cmt_top_r_upper_t.db']

    # Load PIP lists
    print("Loading PIP lists...")
    for piplist in piplists:
        with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                               'cmt_top', piplist)) as f:
            for l in f:
                tile_type, dst, src = l.strip().split('.')
                if tile_type not in pipdata:
                    pipdata[tile_type] = []

                pipdata[tile_type].append((src, dst))

    # Load PPIP lists (to exclude them)
    print("Loading PPIP lists...")
    for ppiplist in ppiplists:
        fname = os.path.join(
            os.getenv('FUZDIR'), '..', '071-ppips', 'build', ppiplist)
        with open(fname, 'r') as f:
            for l in f:
                pip_data, pip_type = l.strip().split()

                if pip_type != 'always':
                    continue

                tile_type, dst, src = pip_data.split('.')
                if tile_type not in ppipdata:
                    ppipdata[tile_type] = []

                ppipdata[tile_type].append((src, dst))

    # Load desgin data
    print("Loading design data...")
    with open("design.txt", "r") as f:
        for line in f:
            fields = line.strip().split(",")
            designdata[fields[0]] = fields[1:]

    with open("design_pips.txt", "r") as f:
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

    tags = {}

    # Populate IN_USE tags
    for tile, (site, in_use) in designdata.items():
        if tile not in tags:
            tags[tile] = {}

        tags[tile]["IN_USE"] = int(in_use)

    # Populate PIPs
    for tile in tags.keys():
        tile_type = tile.rsplit("_", maxsplit=1)[0]

        in_use = tags[tile]["IN_USE"]
        internal_feedback = False

        if not in_use:
            active_pips = []
        else:
            active_pips = tiledata[tile]["pips"]

        for src, dst in pipdata[tile_type]:

            if (src, dst) in ignpip:
                continue
            if (src, dst) in ppipdata[tile_type]:
                continue

            tag = "{}.{}".format(dst, src)
            val = in_use if (src, dst) in active_pips else False

            if not (in_use and not val):
                tags[tile][tag] = int(val)

    # Output tags
    for tile, tile_tags in tags.items():
        for t, v in tile_tags.items():
            segmk.add_tile_tag(tile, t, v)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
