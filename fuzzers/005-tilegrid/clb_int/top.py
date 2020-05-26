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
        if gridinfo.tile_type in ['CLBLL_L', 'CLBLL_R', 'CLBLM_L', 'CLBLM_R']:
            site_name = sorted(gridinfo.sites.keys())[0]
            if gridinfo.tile_type[-1] == 'L':
                int_tile_loc = (loc.grid_x + 1, loc.grid_y)
            else:
                int_tile_loc = (loc.grid_x - 1, loc.grid_y)

            int_tile_name = grid.tilename_at_loc(int_tile_loc)

            if not int_tile_name.startswith('INT_'):
                continue

            yield int_tile_name, site_name


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top(input di, output do);
    assign do = di;
    ''')

    params = {}

    sites = sorted(list(gen_sites()))
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
