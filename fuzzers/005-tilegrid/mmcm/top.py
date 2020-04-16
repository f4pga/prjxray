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
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        gridinfo = grid.gridinfo_at_tilename(tile_name)
        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['MMCME2_ADV']:
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
    # FIXME: can't LOC?
    # only one for now, worry about later
    sites = list(gen_sites())
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        # 0 is invalid
        # shift one bit, keeping LSB constant
        CLKOUT1_DIVIDE = {0: 2, 1: 3}[isone]
        params[tile_name] = (site_name, CLKOUT1_DIVIDE)

        print(
            '''
    (* KEEP, DONT_TOUCH, LOC=%s *)
    MMCME2_ADV #(/*.LOC("%s"),*/ .CLKOUT1_DIVIDE(%u)) dut_%s(
            .CLKFBOUT(),
            .CLKFBOUTB(),
            .CLKFBSTOPPED(),
            .CLKINSTOPPED(),
            .CLKOUT0(),
            .CLKOUT0B(),
            .CLKOUT1(),
            .CLKOUT1B(),
            .CLKOUT2(),
            .CLKOUT2B(),
            .CLKOUT3(),
            .CLKOUT3B(),
            .CLKOUT4(),
            .CLKOUT5(),
            .CLKOUT6(),
            .DO(),
            .DRDY(),
            .LOCKED(),
            .PSDONE(),
            .CLKFBIN(clk),
            .CLKIN1(clk),
            .CLKIN2(clk),
            .CLKINSEL(clk),
            .DADDR(),
            .DCLK(clk),
            .DEN(),
            .DI(),
            .DWE(),
            .PSCLK(clk),
            .PSEN(),
            .PSINCDEC(),
            .PWRDWN(),
            .RST());
''' % (verilog.quote(site_name), site_name, CLKOUT1_DIVIDE, site_name))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
