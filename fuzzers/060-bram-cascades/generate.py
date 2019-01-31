#!/usr/bin/env python3

from prjxray.segmaker import Segmaker

segmk = Segmaker("design.bits")

tiledata = {}
pipdata = {}
ignpip = set()

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        tile, pip, src, dst, pnum, pdir = line.split()

        if not tile.startswith('BRAM_'):
            continue

        # BRAM_R_X37Y0/BRAM_R.BRAM_IMUX35_1->BRAM_R_IMUX_ADDRBWRADDRL2
        pip_prefix, pip = pip.split(".")
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

        if tile_type not in pipdata:
            pipdata[tile_type] = {}

        if pip in pipdata[tile_type]:
            assert pipdata[tile_type][pip] == (src, dst)
        else:
            pipdata[tile_type][pip] = (src, dst)

        tiledata[tile]["pips"].add(pip)
        tiledata[tile]["srcs"].add(src)
        tiledata[tile]["dsts"].add(dst)

        if pdir == 0:
            tiledata[tile]["srcs"].add(dst)
            tiledata[tile]["dsts"].add(src)

        if pnum == 1 or pdir == 0:
            ignpip.add(pip)

for tile, pips_srcs_dsts in tiledata.items():
    tile_type = pips_srcs_dsts["type"]
    pips = pips_srcs_dsts["pips"]
    srcs = pips_srcs_dsts["srcs"]
    dsts = pips_srcs_dsts["dsts"]

    for pip, src_dst in pipdata[tile_type].items():
        src, dst = src_dst

        # BRAM_R has some _R_ added to some pips.  Because BRAM_L and BRAM_R
        # appears to shares all bits, overlap the names during fuzzing to avoid
        # extra work.
        #
        # BRAM.BRAM_ADDRARDADDRL0.BRAM_IMUX_R_ADDRARDADDRL0
        #
        # becomes
        #
        # BRAM.BRAM_ADDRARDADDRL0.BRAM_IMUX_ADDRARDADDRL0
        src_no_r = src.replace('BRAM_R_IMUX_ADDR', 'BRAM_IMUX_ADDR')

        if pip in ignpip:
            pass

        elif pip in pips:
            segmk.add_tile_tag(tile, "%s.%s" % (dst, src_no_r), 1)
        elif src_dst[1] not in dsts:
            segmk.add_tile_tag(tile, "%s.%s" % (dst, src_no_r), 0)

segmk.compile()
segmk.write()
