#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import re

REBUF_GCLK = re.compile('^CLK_BUFG_REBUF_R_CK_GCLK([0-9]+)_BOT$')
def main():
    segmk = Segmaker("design.bits")

    print("Loading tags from design.txt.")

    gclks_in_use = {}
    with open("design.txt", "r") as f:
        for line in f:
            if 'CLK_BUFG_REBUF' not in line:
                continue

            parts = line.replace('{', '').replace('}','').strip().replace('\t', ' ').split(' ')
            dst = parts[0]
            pip = parts[3]

            tile_from_pip, pip = pip.split('/')

            if 'CLK_BUFG_REBUF' not in tile_from_pip:
                continue

            tile_type, pip = pip.split('.')
            assert tile_type == 'CLK_BUFG_REBUF'

            wire_a, wire_b = pip.split('<<->>')

            tile_from_wire, dst = dst.split('/')

            assert dst == wire_a

            m = REBUF_GCLK.match(dst)
            assert m, dst
            gclk = int(m.group(1))

            if tile_from_pip not in gclks_in_use:
                gclks_in_use[tile_from_pip] = set()
            gclks_in_use[tile_from_pip].add(gclk)

            if tile_from_wire == tile_from_pip:
                segmk.add_tile_tag(tile_from_pip, '{}.{}'.format(wire_a, wire_b), wire_a == dst)
                segmk.add_tile_tag(tile_from_pip, '{}.{}'.format(wire_b, wire_a), wire_a != dst)
            else:
                segmk.add_tile_tag(tile_from_pip, '{}.{}'.format(wire_a, wire_b), wire_a != dst)
                segmk.add_tile_tag(tile_from_pip, '{}.{}'.format(wire_b, wire_a), wire_a == dst)

    for tile, gclks in gclks_in_use.items():
        for gclk in range(2):
            segmk.add_tile_tag(tile, 'GCLK{}_ENABLED'.format(gclk), gclk in gclks)

    segmk.compile()
    segmk.write(allow_empty=True)


if __name__ == '__main__':
    main()
