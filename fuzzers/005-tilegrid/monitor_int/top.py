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
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        found_xadc = False
        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['XADC']:
                found_xadc = True
                break

        if not found_xadc:
            continue

        int_grid_x = loc.grid_x + 3
        int_tile_type = 'INT_L'

        int_tile_locs = []
        for dy in range(-1, 1):
            int_tile_locs.append((int_grid_x, loc.grid_y + dy), )

        int_tiles = []
        for int_tile_loc in int_tile_locs:
            int_gridinfo = grid.gridinfo_at_loc(int_tile_loc)
            assert int_gridinfo.tile_type == int_tile_type, (
                int_gridinfo.tile_type, int_tile_type)

            int_tiles.append(grid.tilename_at_loc(int_tile_loc))

        yield tile_name, int_tiles


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, (val) in sorted(params.items()):
        pinstr += '%s,%s\n' % (tile, val)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')

    sites = list(gen_sites())

    # Only on CFG_CENTER_MID expected.
    assert len(sites) == 1
    tile_name, int_tiles = sites[0]

    # int_tiles[0]:
    # IMUX43 -> XADC_CONVST = 0
    # IMUX42 -> XADC_DWE = toggle 0/1
    # int_tiles[1]:
    # IMUX43 -> XADC_DI15 = 0
    # IMUX42 -> XADC_DI14 = toggle 0/1

    DWE = random.randint(0, 1)
    DI14 = random.randint(0, 1)

    params = {}
    params[int_tiles[0]] = DWE
    params[int_tiles[1]] = DI14

    print(
        """
    wire [15:0] di;
    wire dwe;
    wire convst;

    assign convst = 0;
    assign dwe = {DWE};

    assign di[15] = 0;
    assign di[14] = {DI14};

    (* KEEP, DONT_TOUCH *)
    XADC xadc (
        .DI(di),
        .DWE(dwe),
        .CONVST(convst)
    );
    """.format(
            DWE=DWE,
            DI14=DI14,
        ))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
