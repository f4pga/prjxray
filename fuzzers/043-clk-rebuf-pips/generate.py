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
from prjxray.db import Database
from prjxray.util import get_db_root, get_part
import re

REBUF_GCLK = re.compile('^CLK_BUFG_REBUF_R_CK_GCLK([0-9]+)_BOT$')

GCLKS = 32


def gclk_of_wire(wire):
    m = REBUF_GCLK.match(wire)
    assert m, wire
    return int(m.group(1))


class ClockColumn(object):
    def __init__(self, db_root, part):
        db = Database(db_root, part)
        grid = db.grid()

        tiles_in_gclk_columns = []
        self.gclk_columns = {}

        for tile in grid.tiles():
            gridinfo = grid.gridinfo_at_tilename(tile)

            if gridinfo.tile_type != 'CLK_BUFG_REBUF':
                continue

            loc = grid.loc_of_tilename(tile)

            tiles_in_gclk_columns.append((loc.grid_y, tile))

        _, self.tiles_in_gclk_columns = zip(
            *sorted(tiles_in_gclk_columns, key=lambda x: x[0]))

        # Initially all GCLK lines are idle.  GCLK lines only exist between
        #CLK_BUFG_REBUF tiles, hence len-1.
        for gclk in range(GCLKS):
            self.gclk_columns[gclk] = [
                False for _ in range(len(self.tiles_in_gclk_columns) - 1)
            ]

    def enable_rebuf(self, tile, wire):
        # Find which REBUF is being activated.
        rebuf_idx = self.tiles_in_gclk_columns.index(tile)
        assert rebuf_idx != -1, tile

        gclk = gclk_of_wire(wire)

        self.gclk_columns[gclk][rebuf_idx] = True
        self.gclk_columns[gclk][rebuf_idx - 1] = True

    def yield_rebuf_state(self):
        """ Yields tile_name, gclk, bool if active above tile, bool if active below tile """
        for idx, tile in enumerate(self.tiles_in_gclk_columns):
            for gclk in range(GCLKS):
                active_below = False
                active_above = False

                if idx > 0:
                    active_below = self.gclk_columns[gclk][idx - 1]

                if idx < len(self.gclk_columns[gclk]):
                    active_above = self.gclk_columns[gclk][idx]

                yield tile, gclk, active_below, active_above


def main():
    db_root = get_db_root()
    part = get_part()

    clock_column = ClockColumn(db_root, part)

    segmk = Segmaker("design.bits")

    print("Loading tags from design.txt.")

    with open("route.txt", "r") as f:
        for line in f:
            if 'CLK_BUFG_REBUF' not in line:
                continue

            parts = line.replace('{', '').replace('}', '').strip().replace(
                '\t', ' ').split(' ')
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

            if tile_from_wire == tile_from_pip:
                b_to_a = wire_a == dst
                a_to_b = not b_to_a
            else:
                b_to_a = wire_a != dst
                a_to_b = not b_to_a

            segmk.add_tile_tag(
                tile_from_pip, '{}.{}'.format(wire_a, wire_b), b_to_a)
            segmk.add_tile_tag(
                tile_from_pip, '{}.{}'.format(wire_b, wire_a), a_to_b)

            clock_column.enable_rebuf(tile_from_pip, wire_a)

    for tile, gclk, active_below, active_above in clock_column.yield_rebuf_state(
    ):
        segmk.add_tile_tag(
            tile, 'GCLK{}_ENABLE_ABOVE'.format(gclk), active_above)
        segmk.add_tile_tag(
            tile, 'GCLK{}_ENABLE_BELOW'.format(gclk), active_below)

    segmk.compile()
    segmk.write(allow_empty=True)


if __name__ == '__main__':
    main()
