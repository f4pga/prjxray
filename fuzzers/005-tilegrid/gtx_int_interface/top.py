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
import re
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database
from prjxray.grid_types import GridLoc

GTX_INT_Y_RE = re.compile("GTX_INT_INTERFACE.*X[0-9]+Y([0-9]+)")


def get_gtx_int_tile(clock_region, grid):
    for tile_name in sorted(grid.tiles()):
        if not tile_name.startswith("GTX_INT_INTERFACE"):
            continue

        loc = grid.loc_of_tilename(tile_name)

        left_gridinfo = grid.gridinfo_at_loc(
            GridLoc(loc.grid_x - 1, loc.grid_y))
        right_gridinfo = grid.gridinfo_at_loc(
            GridLoc(loc.grid_x + 1, loc.grid_y))

        if left_gridinfo.tile_type in ["INT_L", "INT_R"]:
            cmt = left_gridinfo.clock_region
        elif right_gridinfo.tile_type in ["INT_L", "INT_R"]:
            cmt = right_gridinfo.clock_region
        else:
            assert False

        gridinfo = grid.gridinfo_at_loc(loc)

        m = GTX_INT_Y_RE.match(tile_name)

        assert m

        int_y = int(m.group(1))

        if clock_region == cmt and int_y % 50 == 26:
            return tile_name


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['GTXE2_COMMON']:
                gtx_int_tile = get_gtx_int_tile(gridinfo.clock_region, grid)

                yield gtx_int_tile, site_name


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
    for gtx_int_tile, site_name in sites:
        isone = random.randint(0, 1)

        params[gtx_int_tile] = (site_name, isone)

        print(
            '''
wire QPLLLOCKEN_{site};

(* KEEP, DONT_TOUCH *)
LUT1 lut_{site} (.O(QPLLLOCKEN_{site}));

(* KEEP, DONT_TOUCH, LOC = "{site}" *)
GTXE2_COMMON gtxe2_common_{site} (
    .QPLLLOCKEN(QPLLLOCKEN_{site})
);'''.format(site=site_name))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
