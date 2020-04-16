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
#random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CFG_CENTER_MID']:
            for site_name in sorted(gridinfo.sites.keys()):
                if site_name.startswith("BSCAN_X0Y0"):
                    yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')
    params = {}

    sites = list(gen_sites())
    jtag_chains = ("1", "2", "3", "4")
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)
        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "{0}" *)
            BSCANE2 #(
            .JTAG_CHAIN("{1}")
            )
            BSCANE2_{0} (
            .CAPTURE(),
            .DRCK(),
            .RESET(),
            .RUNTEST(),
            .SEL(),
            .SHIFT(),
            .TCK(),
            .TDI(),
            .TMS(),
            .UPDATE(),
            .TDO(1'b1)
            );
        '''.format(site_name, jtag_chains[isone]))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
