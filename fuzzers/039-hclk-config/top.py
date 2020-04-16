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
from prjxray.db import Database
from prjxray import util
from prjxray.lut_maker import LutMaker


def gen_sites():
    xy_fun = util.create_xy_fun('BUFR_')
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        sites = []

        xs = []
        ys = []
        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFR':
                x, y = xy_fun(site)
                xs.append(x)
                ys.append(y)

                sites.append((site, x, y))

        if not sites:
            continue

        ioi3 = grid.gridinfo_at_loc((loc.grid_x, loc.grid_y - 1))

        if 'IOI3' not in ioi3.tile_type:
            continue

        if ioi3.tile_type.startswith('R'):
            dx = 1
        else:
            assert ioi3.tile_type.startswith('L')
            dx = -1

        iobs = []

        for dy in (-1, -3, 2, 4):
            iob = grid.gridinfo_at_loc((loc.grid_x + dx, loc.grid_y + dy))

            for site, site_type in iob.sites.items():
                if site_type == 'IOB33M':
                    iobs.append(site)

        yield tile_name, min(xs), min(ys), sorted(sites), sorted(iobs)


def main():

    params_list = []
    num_clocks = 0
    outputs = []
    luts = LutMaker()
    for tile_name, x_min, y_min, sites, iobs in gen_sites():
        ioclks = []
        for iob in iobs:
            ioclk = 'clk_{}'.format(iob)
            ioclks.append(ioclk)
            idx = num_clocks
            num_clocks += 1
            outputs.append(
                '''
        wire {ioclk};

        (* KEEP, DONT_TOUCH, LOC="{site}" *)
        IBUF #(
            .IOSTANDARD("LVCMOS33")
            ) ibuf_{site} (
                .I(clks[{idx}]),
                .O({ioclk})
                );'''.format(
                    ioclk=ioclk,
                    site=iob,
                    idx=idx,
                ))

        for site, x, y in sites:
            params = {}
            params['tile'] = tile_name
            params['site'] = site
            params['IN_USE'] = random.randint(0, 1)
            params['x'] = x - x_min
            params['y'] = y - y_min

            if params['IN_USE']:
                params['BUFR_DIVIDE'] = random.choice(
                    (
                        '"BYPASS"',
                        '1',
                        '2',
                        '3',
                        '4',
                        '5',
                        '6',
                        '7',
                        '8',
                    ))
                params['I'] = random.choice(ioclks)

                if params['BUFR_DIVIDE'] == '"BYPASS"':
                    params['CE'] = '1'
                    params['CLR'] = '0'
                else:
                    params['CE'] = luts.get_next_output_net()
                    params['CLR'] = luts.get_next_output_net()

                outputs.append(
                    '''
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFR #(
        .BUFR_DIVIDE({BUFR_DIVIDE})
        ) buf_{site} (
            .CE({CE}),
            .CLR({CLR}),
            .I({I})
        );
                    '''.format(**params))

            params_list.append(params)

    print(
        '''
module top(input [{n1}:0] clks);
    '''.format(n1=num_clocks - 1))

    print("""
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy (
        );""")

    for l in luts.create_wires_and_luts():
        print(l)

    for l in outputs:
        print(l)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params_list, f, indent=2)


if __name__ == '__main__':
    main()
