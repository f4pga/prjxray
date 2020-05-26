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


def gen_dsps():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        sites = []
        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['DSP48E1']:
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

    sites = list(gen_dsps())
    fuzz_iter = iter(util.gen_fuzz_states(len(sites) * 5))
    for tile_name, dsp_sites, int_tiles in sites:
        int_tiles.reverse()

        # Each DSP tile has 5 INT tiles.
        # The following feature is used to toggle a one PIP in each INT tile
        #
        # For a DSP, there are the following INT tiles and the feature
        # to toggle
        #
        # INT_L_X34Y89/INT_L.GFAN1->>IMUX_L30 :: D1.C36 = 0
        # INT_L_X34Y89/INT_L.GFAN1->>IMUX_L28 :: D1.CARRYINSEL1 = toggle
        #
        # INT_L_X34Y88/INT_L.GFAN1->>IMUX_L30 :: D0.CARRYINSEL0 = toggle
        #
        # INT_L_X34Y87/INT_L.GFAN1->>IMUX_L5  :: D1.A29 = 0
        # INT_L_X34Y87/INT_L.GFAN1->>IMUX_L14 :: D1.B8 = toggle
        #
        # INT_L_X34Y86/INT_L.GFAN1->>IMUX_L30 :: D1.B4 = 0
        # INT_L_X34Y86/INT_L.GFAN1->>IMUX_L28 :: D1.B6 = toggle
        #
        # INT_L_X34Y85/INT_L.GFAN1->>IMUX_L30 :: Dark Green :: D1.C20 = 0
        # INT_L_X34Y85/INT_L.GFAN1->>IMUX_L28 :: Color 10 :: D1.B2 = toggle
        (d1_carryinsel1, d0_carryinsel0, d1_b8, d1_b6,
         d1_b2) = itertools.islice(fuzz_iter, 5)
        params[int_tiles[0]] = (d1_carryinsel1, )
        params[int_tiles[1]] = (d0_carryinsel0, )
        params[int_tiles[2]] = (d1_b8, )
        params[int_tiles[3]] = (d1_b6, )
        params[int_tiles[4]] = (d1_b2, )

        print(
            '''
            wire [6:0] {dsp_site0}_opmode;
            wire [2:0] {dsp_site0}_carryinsel;

            wire [29:0] {dsp_site1}_a;
            wire [17:0] {dsp_site1}_b;
            wire [47:0] {dsp_site1}_c;
            wire [6:0] {dsp_site1}_opmode;
            wire [2:0] {dsp_site1}_carryinsel;

            // INT 0, {int0}
            assign {dsp_site1}_c[36] = 0;
            assign {dsp_site1}_carryinsel[1] = {d1_carryinsel1};

            // INT 1, {int1}
            assign {dsp_site0}_carryinsel[0] = {d0_carryinsel0};

            // INT 2, {int2}
            assign {dsp_site1}_a[29] = 0;
            assign {dsp_site1}_b[8] = {d1_b8};

            // INT 3, {int3}
            assign {dsp_site1}_b[4] = 0;
            assign {dsp_site1}_b[6] = {d1_b6};

            // INT 4, {int4}
            assign {dsp_site1}_c[20] = 0;
            assign {dsp_site1}_b[2] = {d1_b2};

            (* KEEP, DONT_TOUCH, LOC = "{dsp_site0}" *)
            DSP48E1 #(
                    .OPMODEREG(0),
                    .CREG(0)
                ) dsp_{dsp_site0} (
                    .OPMODE({dsp_site0}_opmode),
                    .CARRYINSEL({dsp_site0}_carryinsel)
                    );

            (* KEEP, DONT_TOUCH, LOC = "{dsp_site1}" *)
            DSP48E1 #(
                    .OPMODEREG(0),
                    .CREG(0)
                ) dsp_{dsp_site1} (
                    .OPMODE({dsp_site1}_opmode),
                    .CARRYINSEL({dsp_site1}_carryinsel),
                    .A({dsp_site1}_a),
                    .B({dsp_site1}_b),
                    .C({dsp_site1}_c)
                    );
'''.format(
                dsp_site0=dsp_sites[0],
                dsp_site1=dsp_sites[1],
                d1_carryinsel1=d1_carryinsel1,
                d0_carryinsel0=d0_carryinsel0,
                d1_b8=d1_b8,
                d1_b6=d1_b6,
                d1_b2=d1_b2,
                int0=int_tiles[0],
                int1=int_tiles[1],
                int2=int_tiles[2],
                int3=int_tiles[3],
                int4=int_tiles[4],
            ))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
