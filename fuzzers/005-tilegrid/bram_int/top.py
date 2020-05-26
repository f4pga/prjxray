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


def gen_brams():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        sites = []
        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['RAMB18E1', 'FIFO18E1']:
                sites.append(site_name)

        sites.sort()

        if len(sites) == 0:
            continue

        if gridinfo.tile_type[-1] == 'L':
            int_grid_x = loc.grid_x + 2
            int_tile_type = 'INT_L'
        else:
            int_grid_x = loc.grid_x - 2
            int_tile_type = 'INT_R'

        int_tile_locs = [
            (int_grid_x, loc.grid_y),
            (int_grid_x, loc.grid_y - 1),
            (int_grid_x, loc.grid_y - 2),
            (int_grid_x, loc.grid_y - 3),
            (int_grid_x, loc.grid_y - 4),
        ]

        int_tiles = []
        for int_tile_loc in int_tile_locs:
            int_gridinfo = grid.gridinfo_at_loc(int_tile_loc)
            assert int_gridinfo.tile_type == int_tile_type, (
                int_gridinfo.tile_type, int_tile_type)

            int_tiles.append(grid.tilename_at_loc(int_tile_loc))

        yield tile_name, sites, int_tiles


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

    sites = list(gen_brams())
    fuzz_iter = iter(util.gen_fuzz_states(len(sites) * 5))
    for tile_name, bram_sites, int_tiles in sites:
        # Each BRAM tile has 5 INT tiles.
        # The following feature is used to toggle a one PIP in each INT tile
        #
        # For BRAM_L_X6Y0, there are the following INT tiles and the feature
        # to toggle
        #
        #  - INT_L_X6Y0, tie bram_sites[0].DIADI[2] = 0, toggle bram_sites[0].DIADI[3]
        #  - INT_L_X6Y1, tie bram_sites[1].ADDRBWRADDR[7] = 0, toggle bram_sites[1].ADDRBWRADDR[10]
        #  - INT_L_X6Y2, tie bram_sites[1].ADDRARDADDR[9] = 0, toggle bram_sites[1].ADDRBWRADDR[9]
        #  - INT_L_X6Y3, tie bram_sites[1].ADDRBWRADDR[4] = 0, toggle bram_sites[1].ADDRBWRADDR[13]
        #  - INT_L_X6Y4, tie bram_sites[1].DIBDI[15] = 0, toggle bram_sites[1].DIADI[7]
        (b0_diadi3, b1_wraddr10, b1_wraddr9, b1_wraddr13,
         b1_diadi7) = itertools.islice(fuzz_iter, 5)
        params[int_tiles[0]] = (b0_diadi3, )
        params[int_tiles[1]] = (b1_wraddr10, )
        params[int_tiles[2]] = (b1_wraddr9, )
        params[int_tiles[3]] = (b1_wraddr13, )
        params[int_tiles[4]] = (b1_diadi7, )

        print(
            '''
            wire [15:0] {bram_site0}_diadi;
            wire [15:0] {bram_site0}_dibdi;
            wire [13:0] {bram_site0}_wraddr;

            wire [15:0] {bram_site1}_diadi;
            wire [15:0] {bram_site1}_dibdi;
            wire [7:0] {bram_site1}_webwe;
            wire [13:0] {bram_site1}_rdaddr;
            wire [13:0] {bram_site1}_wraddr;

            // INT 0
            assign {bram_site0}_diadi[2] = 0;
            assign {bram_site0}_diadi[3] = {b0_diadi3};

            // INT 1
            assign {bram_site1}_wraddr[7] = 0;
            assign {bram_site1}_wraddr[10] = {b1_wraddr10};

            // INT 2
            assign {bram_site1}_rdaddr[9] = 0;
            assign {bram_site1}_wraddr[9] = {b1_wraddr9};

            // INT 3
            assign {bram_site1}_wraddr[4] = 0;
            assign {bram_site1}_wraddr[13] = {b1_wraddr13};

            // INT 4
            assign {bram_site1}_dibdi[15] = 0;
            assign {bram_site1}_diadi[7] = {b1_diadi7};

            (* KEEP, DONT_TOUCH, LOC = "{bram_site0}" *)
            RAMB18E1 #(
                ) bram_{bram_site0} (
                    .CLKARDCLK(),
                    .CLKBWRCLK(),
                    .ENARDEN(),
                    .ENBWREN(),
                    .REGCEAREGCE(),
                    .REGCEB(),
                    .RSTRAMARSTRAM(),
                    .RSTRAMB(),
                    .RSTREGARSTREG(),
                    .RSTREGB(),
                    .ADDRARDADDR(),
                    .ADDRBWRADDR({bram_site0}_wraddr),
                    .DIADI({bram_site0}_diadi),
                    .DIBDI({bram_site0}_dibdi),
                    .DIPADIP(),
                    .DIPBDIP(),
                    .WEA(),
                    .WEBWE(),
                    .DOADO(),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());

            (* KEEP, DONT_TOUCH, LOC = "{bram_site1}" *)
            RAMB18E1 #(
                ) bram_{bram_site1} (
                    .CLKARDCLK(),
                    .CLKBWRCLK(),
                    .ENARDEN(),
                    .ENBWREN(),
                    .REGCEAREGCE(),
                    .REGCEB(),
                    .RSTRAMARSTRAM(),
                    .RSTRAMB(),
                    .RSTREGARSTREG(),
                    .RSTREGB(),
                    .ADDRARDADDR({bram_site1}_rdaddr),
                    .ADDRBWRADDR({bram_site1}_wraddr),
                    .DIADI({bram_site1}_diadi),
                    .DIBDI({bram_site1}_dibdi),
                    .DIPADIP(),
                    .DIPBDIP(),
                    .WEA(),
                    .WEBWE({bram_site1}_webwe),
                    .DOADO(),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());
'''.format(
                bram_site0=bram_sites[0],
                bram_site1=bram_sites[1],
                b0_diadi3=b0_diadi3,
                b1_wraddr10=b1_wraddr10,
                b1_wraddr9=b1_wraddr9,
                b1_wraddr13=b1_wraddr13,
                b1_diadi7=b1_diadi7))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
