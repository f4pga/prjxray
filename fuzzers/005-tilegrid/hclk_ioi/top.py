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
        sites = []
        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFR':
                sites.append(site)

        if sites:
            yield tile_name, sorted(sites)


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
    for (tile_name, sites), isone in zip(sites,
                                         util.gen_fuzz_states(len(sites))):
        site_name = sites[0]
        params[tile_name] = (site_name, isone)

        print(
            '''
            wire clk_{site};
            BUFMRCE buf_{site} (
                .O(clk_{site})
            );

            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            BUFR #(
                .BUFR_DIVIDE("{divide}")
                ) bufr_{site} (
                .I(clk_{site})
                );
'''.format(site=site_name, divide="2" if isone else "1"))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
