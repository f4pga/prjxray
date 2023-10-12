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
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import lut_maker
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        if not 'CFG_CENTER_MID' in tile_name:
            continue
        print("// tile: " + str(tile_name))
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        sites = {}
        print("// " + str(gridinfo.sites.items()))
        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'STARTUP':
                print("// got site: " + str(site_name))
                sites[site_type] = site_name

        if sites:
            yield tile_name, sites

def run():
    params = {
        "tiles": [],
    }

    for tile, sites in gen_sites():
        for site_type, site in sites.items():
            p = {}
            p['tile'] = tile
            p['site'] = site

            p['CONNECTION'] = random.choice(
                (
                    'HARD_ZERO',
                    # hard zero or hard one does not make a difference
                    # it only seems to matter if it is connected to a clock net or not
                    #'HARD_ONE',
                    'CLOCK',
                ))

            params['tiles'].append(p)

    print(
    '''
module top (input  wire clk);
    (* KEEP, DONT_TOUCH *)
    STARTUPE2 STARTUPE2 (
        .CLK(1'b0),
        .GSR(1'b0),
        .GTS(1'b0),
        .KEYCLEARB(1'b1),
        .PACK(1'b0),
        .PREQ(),
  
        // Drive clock.''')

    connection = p['CONNECTION']

    if connection == "HARD_ZERO":
        print("        .USRCCLKO (1'b0),")
    elif connection == "HARD_ONE":
        print("        .USRCCLKO (1'b1),")
    else:    
        print("        .USRCCLKO (clk),")

    print(
    '''
        .USRCCLKTS(1'b0),  
        .USRDONEO (1'b0),
        .USRDONETS(1'b1),
        .CFGCLK(),
        .CFGMCLK(),
        .EOS()
    );

endmodule
''')

    with open('params.json', 'w') as f:
        json.dump(params, f, indent=2)

if __name__ == '__main__':
    run()
