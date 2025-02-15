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

PCIE_INT_Y_RE = re.compile("PCIE_INT_INTERFACE.*X[0-9]+Y([0-9]+)")


def get_pcie_int_tiles(grid, pcie_loc):
    def get_site_at_loc(loc):
        gridinfo = grid.gridinfo_at_loc(loc)

        sites = list(gridinfo.sites.keys())

        if len(sites) and sites[0].startswith("SLICE"):
            return sites[0]

        return None

    pcie_int_tiles = list()

    for tile_name in sorted(grid.tiles()):
        if not tile_name.startswith("PCIE_INT_INTERFACE"):
            continue

        m = PCIE_INT_Y_RE.match(tile_name)

        assert m

        int_y = int(m.group(1))

        if int_y % 50 == 0:
            loc = grid.loc_of_tilename(tile_name)
            is_left = loc.grid_x < pcie_loc.grid_x

            if is_left:
                for i in range(1, loc.grid_x):
                    loc_grid_x = loc.grid_x - i

                    site = get_site_at_loc(GridLoc(loc_grid_x, loc.grid_y))

                    if site:
                        break
            else:
                _, x_max, _, _ = grid.dims()
                for i in range(1, x_max - loc.grid_x):
                    loc_grid_x = loc.grid_x + i

                    site = get_site_at_loc(GridLoc(loc_grid_x, loc.grid_y))

                    if site:
                        break

            pcie_int_tiles.append((tile_name, is_left, site))

    return pcie_int_tiles


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['PCIE_2_1']:
                pcie_int_tiles = get_pcie_int_tiles(grid, loc)

                yield pcie_int_tiles, site_name


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
    for pcie_int_tiles, site_name in sites:
        left_side = None
        right_side = None

        for tile, is_left, site in pcie_int_tiles:
            isone = random.randint(0, 1)
            params[tile] = (site_name, isone)

            if is_left:
                left_side = site
            else:
                right_side = site

        assert left_side and right_side

        print(
            '''
wire [1:0] PLDIRECTEDLINKCHANGE;
wire [68:0] MIMTXRDATA;

(* KEEP, DONT_TOUCH, LOC = "{left}" *)
LUT1 left_lut_{left} (.O(MIMTXRDATA[0]));

(* KEEP, DONT_TOUCH, LOC = "{right}" *)
LUT1 right_lut_{right} (.O(PLDIRECTEDLINKCHANGE[0]));

(* KEEP, DONT_TOUCH, LOC = "{site}" *)
PCIE_2_1 pcie_2_1_{site} (
    .PLDIRECTEDLINKCHANGE(PLDIRECTEDLINKCHANGE),
    .MIMTXRDATA(MIMTXRDATA)
);'''.format(site=site_name, right=right_side, left=left_side))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
