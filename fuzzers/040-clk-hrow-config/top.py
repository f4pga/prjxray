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
import json
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    get_xy = util.create_xy_fun('BUFHCE_')
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        sites = []

        xs = []
        ys = []
        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFHCE':
                x, y = get_xy(site)
                xs.append(x)
                ys.append(y)

                sites.append((site, x, y))

        if sites:
            yield tile_name, min(xs), min(ys), sorted(sites)


def main():
    print('''
module top();
    ''')

    params_list = []
    for tile_name, x_min, y_min, sites in gen_sites():

        for site, x, y in sites:
            params = {}
            params['tile'] = tile_name
            params['site'] = site
            params['x'] = x - x_min
            params['y'] = y - y_min
            params['IN_USE'] = random.randint(0, 1)

            if params['IN_USE']:
                params['INIT_OUT'] = random.randint(0, 1)
                params['CE_TYPE'] = verilog.quote(
                    random.choice(('SYNC', 'ASYNC')))
                params['IS_CE_INVERTED'] = random.randint(0, 1)
                print(
                    '''
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFHCE #(
        .INIT_OUT({INIT_OUT}),
        .CE_TYPE({CE_TYPE}),
        .IS_CE_INVERTED({IS_CE_INVERTED})
        ) buf_{site} ();
                    '''.format(**params))

            params_list.append(params)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params_list, f, indent=2)


if __name__ == '__main__':
    main()
