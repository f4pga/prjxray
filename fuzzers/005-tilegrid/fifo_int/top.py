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
import os
import random
import itertools
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_fifos():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['IN_FIFO']:
                if gridinfo.tile_type[-1] == 'L':
                    int_grid_x = loc.grid_x + 2
                    int_tile_type = 'INT_L'
                else:
                    int_grid_x = loc.grid_x - 2
                    int_tile_type = 'INT_R'

                int_tile_locs = [
                    (int_grid_x, loc.grid_y + idx - 5) for idx in range(12)
                ]

                int_tiles = []
                for int_tile_loc in int_tile_locs:
                    int_gridinfo = grid.gridinfo_at_loc(int_tile_loc)
                    assert int_gridinfo.tile_type == int_tile_type, (
                        int_tile_loc, int_gridinfo.tile_type, int_tile_type)

                    int_tiles.append(grid.tilename_at_loc(int_tile_loc))

                yield site_name, int_tiles


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, (val, ) in sorted(params.items()):
        pinstr += '%s,%s\n' % (tile, val)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')

    params = {}

    sites = list(gen_fifos())
    N_INT = 12

    fuzz_iter = iter(util.gen_fuzz_states(len(sites) * N_INT))
    for site, int_tiles in sites:
        assert len(int_tiles) == N_INT
        int_tiles.reverse()

        bits = itertools.islice(fuzz_iter, N_INT)

        assigns = []

        # CMT_FIFO mux usage is regular with IMUX_L40 and IMUX_L42.
        #
        # INT[idx].IMUX_L40 = IN.D{idx}[1]
        # INT[idx].IMUX_L42 = IN.D{idx}[3]
        CHANNEL = [0, 1, 2, 3, 4, 5, 5, 6, 6, 7, 8, 9]
        HOLD_BIT_0 = [1, 1, 1, 1, 1, 1, 5, 5, 1, 1, 1, 1]
        TOGGLE_BIT = [3, 3, 3, 3, 3, 3, 7, 7, 3, 3, 3, 3]
        #             0  1  2  3  4  5  6  7  8  9
        WIDTH = [4, 4, 4, 4, 4, 8, 8, 4, 4, 4]

        bits_set = set()

        for idx, (int_tile, bit) in enumerate(zip(int_tiles, bits)):
            bits_set.add((CHANNEL[idx], HOLD_BIT_0[idx]))
            bits_set.add((CHANNEL[idx], TOGGLE_BIT[idx]))

            assigns.append('            // {}'.format(int_tile))
            assigns.append(
                '            assign {site}_in_d{channel}[{bit}] = 0;'.format(
                    site=site,
                    channel=CHANNEL[idx],
                    bit=HOLD_BIT_0[idx],
                ))
            assigns.append(
                '            assign {site}_in_d{channel}[{bit}] = {toggle_bit};'
                .format(
                    site=site,
                    channel=CHANNEL[idx],
                    bit=TOGGLE_BIT[idx],
                    toggle_bit=bit,
                ))
            params[int_tile] = (bit, )

            assigns.append('')

        for channel, width in enumerate(WIDTH):
            for bit in range(width):
                if (channel, bit) not in bits_set:
                    assigns.append(
                        '            assign {site}_in_d{channel}[{bit}] = 1;'.
                        format(
                            site=site,
                            channel=channel,
                            bit=bit,
                        ))

        print(
            '''
            wire [3:0] {site}_in_d0;
            wire [3:0] {site}_in_d1;
            wire [3:0] {site}_in_d2;
            wire [3:0] {site}_in_d3;
            wire [3:0] {site}_in_d4;
            wire [7:0] {site}_in_d5;
            wire [7:0] {site}_in_d6;
            wire [3:0] {site}_in_d7;
            wire [3:0] {site}_in_d8;
            wire [3:0] {site}_in_d9;

{assign_statements}

            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            IN_FIFO fifo_{site} (
                .D0({site}_in_d0),
                .D1({site}_in_d1),
                .D2({site}_in_d2),
                .D3({site}_in_d3),
                .D4({site}_in_d4),
                .D5({site}_in_d5),
                .D6({site}_in_d6),
                .D7({site}_in_d7),
                .D8({site}_in_d8),
                .D9({site}_in_d9)
                );
'''.format(
                site=site,
                assign_statements='\n'.join(assigns),
            ))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
