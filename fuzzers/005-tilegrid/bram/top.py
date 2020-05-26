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

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['FIFO18E1']:
                yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print(
        '''
module top(input clk, stb, di, output do);
    localparam integer DIN_N = 8;
    localparam integer DOUT_N = 8;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];
    ''')

    params = {}

    sites = list(gen_sites())
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)

        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "%s" *)
            RAMB18E1 #(
                    .DOA_REG(%u)
                ) bram_%s (
                    .CLKARDCLK(),
                    .CLKBWRCLK(),
                    .ENARDEN(),
                    .ENBWREN(),
                    .REGCEAREGCE(),
                    .REGCEB(),
                    .RSTRAMARSTRAM(),
                    .RSTRAMB(),
                    .RSTREGARSTREG(),
                    .RSTREGB(),
                    .ADDRARDADDR(),
                    .ADDRBWRADDR(),
                    .DIADI(),
                    .DIBDI(),
                    .DIPADIP(),
                    .DIPBDIP(),
                    .WEA(),
                    .WEBWE(),
                    .DOADO(),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());
''' % (site_name, isone, site_name))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
