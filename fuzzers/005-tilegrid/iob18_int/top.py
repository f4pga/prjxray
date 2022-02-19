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
'''
Generate a primitive to place at every I/O
Unlike CLB tests, the LFSR for this is inside the ROI, not driving it
'''

import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database
import re


def gen_sites():
    '''
    IOB18S: main IOB of a diff pair
    IOB18M: secondary IOB of a diff pair
    IOB18: not a diff pair. Relatively rare (at least in ROI...2 of them?)
    Focus on IOB18S to start
    '''
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        sites = []
        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'IDELAYE2_FINEDELAY':
                sites.append(site_name)

        if len(sites) == 0:
            continue

        sites_y = [
            int(re.match('IDELAY_X[0-9]+Y([0-9]+)', site).group(1))
            for site in sites
        ]

        sites, _ = zip(*sorted(zip(sites, sites_y), key=lambda x: x[1]))

        if gridinfo.tile_type[0] == 'L':
            int_grid_x = loc.grid_x + 3
            pad_grid_x = loc.grid_x - 1
            int_tile_type = 'INT_L'
        else:
            int_grid_x = loc.grid_x - 3
            pad_grid_x = loc.grid_x + 1
            int_tile_type = 'INT_R'

        int_tile_locs = [
            (int_grid_x, loc.grid_y),
        ]

        pad_gridinfo = grid.gridinfo_at_loc((pad_grid_x, loc.grid_y))

        pad_sites = pad_gridinfo.sites.keys()
        pad_sites_y = [
            int(re.match('IOB_X[0-9]+Y([0-9]+)', site).group(1))
            for site in pad_sites
        ]
        pad_sites, _ = zip(
            *sorted(zip(pad_sites, pad_sites_y), key=lambda x: x[1]))

        if not gridinfo.tile_type.endswith("_SING"):
            int_tile_locs.append((int_grid_x, loc.grid_y - 1))

        assert len(sites) == len(int_tile_locs), (
            tile_name, sites, int_tile_locs)
        assert len(sites) == len(pad_sites), (sites, pad_sites)

        for site_name, pad_site, int_tile_loc in zip(sites, pad_sites,
                                                     int_tile_locs):
            int_tile_name = grid.tilename_at_loc(int_tile_loc)
            assert int_tile_name.startswith(int_tile_type), (
                int_tile_name, site_name, int_tile_loc)
            yield int_tile_name, site_name, pad_site


def write_params(params):
    pinstr = ''
    for tile, (site, val, pad_site_name, pin) in sorted(params.items()):
        pinstr += '%s,%s,%s,%s,%s\n' % (tile, val, site, pad_site_name, pin)
    open('params.csv', 'w').write(pinstr)


def run():
    sites = list(gen_sites())
    print(
        '''
`define N_DI {}

module top(input wire [`N_DI-1:0] di);
    wire [`N_DI-1:0] di_buf;

    (* KEEP, DONT_TOUCH, IODELAY_GROUP = "iodelays" *)
    IDELAYCTRL idelayctrl (
        .REFCLK()
    );
    '''.format(len(sites)))

    params = {}

    for idx, ((tile_name, site_name, pad_site_name), isone) in enumerate(zip(
            sites, util.gen_fuzz_states(len(sites)))):
        params[tile_name] = (site_name, isone, pad_site_name, "di[%u]" % idx)

        # Force HARD0 -> GFAN1 with CNTVALUEIN4 = 0
        # Toggle 1 pip with CNTVALUEIN3 = ?
        print(
            '''

            // Solving for {3}
            (* KEEP, DONT_TOUCH *)
            IBUF ibuf_{0}(.I(di[{2}]), .O(di_buf[{2}]));

            (* KEEP, DONT_TOUCH, LOC = "{0}", IODELAY_GROUP = "iodelays" *)
            IDELAYE2 idelay_{0} (
                .CNTVALUEIN(5'b0{1}111),
                .IDATAIN(di_buf[{2}])
                );
'''.format(site_name, isone, idx, tile_name))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
