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


def gen_sites():
    for _tile_name, site_name, _site_type in sorted(util.get_roi().gen_sites(
        ["XADC"])):
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
        "INIT_43": random.randint(0x000, 0xFFFF),
    }

    modname = "my_XADC"
    verilog.instance(modname, "inst_%u" % loci, ports, params=params)
    # LOC isn't support
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
module my_XADC (input clk, input [7:0] din, output [7:0] dout);
    parameter INIT_43 = 16'h0000;

    (* KEEP, DONT_TOUCH *)
    XADC #(
        .INIT_43(INIT_43)
        ) dut (
            .BUSY(),
            .DRDY(),
            .EOC(),
            .EOS(),
            .JTAGBUSY(),
            .JTAGLOCKED(),
            .JTAGMODIFIED(),
            .OT(),
            .DO(),
            .ALM(),
            .CHANNEL(),
            .MUXADDR(),
            .CONVST(),
            .CONVSTCLK(clk),
            .DCLK(clk),
            .DEN(),
            .DWE(),
            .RESET(),
            .VN(),
            .VP(),
            .DI(),
            .VAUXN(),
            .VAUXP(),
            .DADDR());
endmodule
''')
