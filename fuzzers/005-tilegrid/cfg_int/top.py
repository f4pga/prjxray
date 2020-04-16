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

        if gridinfo.tile_type != 'CFG_CENTER_MID':
            continue

        sites = {}
        for site_name, site_type in gridinfo.sites.items():
            if site_type not in sites:
                sites[site_type] = []
            sites[site_type].append(site_name)

        for site_type in sites:
            sites[site_type].sort()

        int_grid_x = loc.grid_x + 3
        int_tile_type = 'INT_L'

        int_tile_locs = []
        for dy in range(-9, 12):
            # Skip the VBREAK tile.
            if dy != 6:
                int_tile_locs.append((int_grid_x, loc.grid_y + dy), )

        int_tiles = []
        for int_tile_loc in int_tile_locs:
            int_gridinfo = grid.gridinfo_at_loc(int_tile_loc)
            assert int_gridinfo.tile_type == int_tile_type, (
                int_gridinfo.tile_type, int_tile_type)

            int_tiles.append(grid.tilename_at_loc(int_tile_loc))

        yield tile_name, sites, int_tiles


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
    tile_name, sites, int_tiles = sites[0]

    assert len(sites['ICAP']) == 2, len(sites['ICAP'])

    # int_tiles[6]:
    # IMUX43 -> ICAP1_I31 = 0
    # IMUX42 -> ICAP1_I30 = toggle 0/1
    # int_tiles[7]:
    # IMUX43 -> ICAP1_I15 = 0
    # IMUX42 -> ICAP1_I14 = toggle 0/1
    # int_tiles[8]:
    # IMUX43 -> ICAP1_CSIB = 0
    # IMUX42 -> ICAP1_RDWRB = toggle 0/1

    ICAP1_I30 = random.randint(0, 1)
    ICAP1_I14 = random.randint(0, 1)
    ICAP1_RDWRB = random.randint(0, 1)

    params = {}
    params[int_tiles[6]] = ICAP1_I30
    params[int_tiles[7]] = ICAP1_I14
    params[int_tiles[8]] = ICAP1_RDWRB

    print(
        """
    wire [31:0] icap_i_{site};
    wire icap_rdwrd_{site};
    wire icap_csib_{site};

    assign icap_i_{site}[31] = 0;
    assign icap_i_{site}[30] = {ICAP1_I30};

    assign icap_i_{site}[15] = 0;
    assign icap_i_{site}[14] = {ICAP1_I14};

    assign icap_csib_{site} = 0;
    assign icap_rdwrb_{site} = {ICAP1_RDWRB};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    ICAPE2 icap_{site} (
        .I(icap_i_{site}),
        .RDWRB(icap_rdwrb_{site}),
        .CSIB(icap_csib_{site})
    );
    """.format(
            site=sites['ICAP'][1],
            ICAP1_I30=ICAP1_I30,
            ICAP1_I14=ICAP1_I14,
            ICAP1_RDWRB=ICAP1_RDWRB))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
