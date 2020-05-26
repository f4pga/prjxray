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
from prjxray.verilog import vrandbit, vrandbits
import sys
import json
import numpy as np


def gen_sites():
    for _tile_name, site_name, _site_type in sorted(util.get_roi().gen_sites(
        ["MMCME2_ADV"])):
        yield site_name


sites = list(gen_sites())
DUTN = len(sites)
DIN_N = DUTN * 8
DOUT_N = DUTN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.jl', 'w')
f.write('module,loc,params\n')
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))

for loci, site in enumerate(sites):

    ports = {
        'clk': 'clk',
        'din': 'din[  %d +: 8]' % (8 * loci, ),
        'dout': 'dout[  %d +: 8]' % (8 * loci, ),
    }

    params = {
        "CLKOUT1_DIVIDE":
        int(
            np.random.choice(
                [1, 63, 127, 128, random.randint(2, 127)],
                p=[0.2, 0.1, 0.1, 0.1,
                   0.5])),  # make sure that special values are present
        "STARTUP_WAIT":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT4_CASCADE":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "STARTUP_WAIT":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKFBOUT_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT0_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT1_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT2_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT3_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT4_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT5_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
        "CLKOUT6_USE_FINE_PS":
        random.choice(["\"TRUE\"", "\"FALSE\""]),
    }

    modname = "my_MMCME2_ADV"
    verilog.instance(modname, "inst_%u" % loci, ports, params=params)
    # LOC isn't supported
    params["LOC"] = verilog.quote(site)

    j = {'module': modname, 'i': loci, 'params': params}
    f.write('%s\n' % (json.dumps(j)))
    print('')

f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module my_MMCME2_ADV (input clk, input [7:0] din, output [7:0] dout);
    parameter CLKOUT1_DIVIDE = 1;
    parameter CLKOUT2_DIVIDE = 1;
    parameter CLKOUT3_DIVIDE = 1;
    parameter CLKOUT4_DIVIDE = 1;
    parameter CLKOUT5_DIVIDE = 1;
    parameter CLKOUT6_DIVIDE = 1;
    parameter DIVCLK_DIVIDE = 1;
    parameter CLKFBOUT_MULT = 5;
    parameter CLKOUT4_CASCADE = "FALSE";
    parameter STARTUP_WAIT = "FALSE";
    parameter CLKFBOUT_USE_FINE_PS = "FALSE";
    parameter CLKOUT0_USE_FINE_PS = "FALSE";
    parameter CLKOUT1_USE_FINE_PS = "FALSE";
    parameter CLKOUT2_USE_FINE_PS = "FALSE";
    parameter CLKOUT3_USE_FINE_PS = "FALSE";
    parameter CLKOUT4_USE_FINE_PS = "FALSE";
    parameter CLKOUT5_USE_FINE_PS = "FALSE";
    parameter CLKOUT6_USE_FINE_PS = "FALSE";

    (* KEEP, DONT_TOUCH *)
    MMCME2_ADV #(
            .CLKOUT1_DIVIDE(CLKOUT1_DIVIDE),
            .CLKOUT2_DIVIDE(CLKOUT2_DIVIDE),
            .CLKOUT3_DIVIDE(CLKOUT3_DIVIDE),
            .CLKOUT4_DIVIDE(CLKOUT4_DIVIDE),
            .CLKOUT5_DIVIDE(CLKOUT5_DIVIDE),
            .CLKOUT6_DIVIDE(CLKOUT6_DIVIDE),
            .CLKOUT4_CASCADE(CLKOUT4_CASCADE),
            .STARTUP_WAIT(STARTUP_WAIT),
            .CLKFBOUT_USE_FINE_PS(CLKFBOUT_USE_FINE_PS),
            .CLKOUT0_USE_FINE_PS(CLKOUT0_USE_FINE_PS),
            .CLKOUT1_USE_FINE_PS(CLKOUT1_USE_FINE_PS),
            .CLKOUT2_USE_FINE_PS(CLKOUT2_USE_FINE_PS),
            .CLKOUT3_USE_FINE_PS(CLKOUT3_USE_FINE_PS),
            .CLKOUT4_USE_FINE_PS(CLKOUT4_USE_FINE_PS),
            .CLKOUT5_USE_FINE_PS(CLKOUT5_USE_FINE_PS),
            .CLKOUT6_USE_FINE_PS(CLKOUT6_USE_FINE_PS)
    ) dut(
            .CLKFBOUT(),
            .CLKFBOUTB(),
            .CLKFBSTOPPED(),
            .CLKINSTOPPED(),
            .CLKOUT0(dout[0]),
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
            .RST(din[0]));
endmodule
''')
