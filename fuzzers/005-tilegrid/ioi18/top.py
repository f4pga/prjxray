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
import io
import os
import random
import re
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import lut_maker
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type.endswith("_SING"):
            continue
        # Y9 tiles have frame address 1 frame higher than the rest
        # Need to investigate what is so special about them
        if tile_name.endswith("Y9"):
            continue

        sites = []
        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'IDELAYE2_FINEDELAY':
                yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,isone,site\n'
    for vals in params:
        pinstr += ','.join(map(str, vals)) + '\n'

    open('params.csv', 'w').write(pinstr)


def use_idelay(p, luts, connects):
    print(
        '''
    wire idelay_{site};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    IDELAYE2_FINEDELAY #(
        .HIGH_PERFORMANCE_MODE("{param}"),
        .DELAY_SRC("DATAIN")
    ) idelay_site_{site} (
        .DATAIN({onet}),
        .DATAOUT(idelay_{site})
        );
    assign {net} = idelay_{site};
       '''.format(
            onet=luts.get_next_output_net(),
            net=luts.get_next_input_net(),
            param="TRUE" if p['isone'] else "FALSE",
            **p),
        file=connects)


def run():
    luts = lut_maker.LutMaker()
    connects = io.StringIO()

    tile_params = []
    params = []
    sites = sorted(list(gen_sites()))
    for idx, ((tile, site), isone) in enumerate(zip(
            sites, util.gen_fuzz_states(len(sites)))):

        p = {}
        p['tile'] = tile
        p['site'] = site
        p['isone'] = isone
        params.append(p)
        tile_params.append((tile, p['isone'], site))

    write_params(tile_params)

    print('''
module top();
    ''')

    # Always output a LUT6 to make placer happy.
    print('''
     (* KEEP, DONT_TOUCH *)
     LUT6 dummy_lut();
     ''')

    # Need IDELAYCTRL for IDEALAYs
    print('''
     (* KEEP, DONT_TOUCH *)
     IDELAYCTRL();
     ''')

    for p in params:
        use_idelay(p, luts, connects)

    for l in luts.create_wires_and_luts():
        print(l)

    print(connects.getvalue())

    print("endmodule")


if __name__ == '__main__':
    run()
