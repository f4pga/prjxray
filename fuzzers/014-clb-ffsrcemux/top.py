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
import random
random.seed(0)
import os
import re
from prjxray import util
from prjxray import verilog

# INCREMENT is the amount of additional CLBN to be instantiated in the design.
# This makes the fuzzer compilation more robust against failures.
INCREMENT = os.getenv('CLBN', 0)
CLBN = 600 + int(INCREMENT)
print('//Requested CLBs: %s' % str(CLBN))


def gen_slices():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEL', 'SLICEM']):
        yield site_name


DIN_N = CLBN * 4
DOUT_N = CLBN * 1
ffprims = ('FDRE', )
ff_bels = (
    'AFF',
    'A5FF',
    'BFF',
    'B5FF',
    'CFF',
    'C5FF',
    'DFF',
    'D5FF',
)

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('name,loc,ce,r\n')
slices = gen_slices()
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    ffprim = random.choice(ffprims)
    force_ce = random.randint(0, 1)
    force_r = random.randint(0, 1)
    # clb_FD clb_FD (.clk(clk), .din(din[  0 +: 4]), .dout(dout[  0]));
    # clb_FD_1 clb_FD_1 (.clk(clk), .din(din[  4 +: 4]), .dout(dout[  1]));
    loc = next(slices)
    #bel = random.choice(ff_bels)
    bel = "AFF"
    name = 'clb_%s' % ffprim
    print('    %s' % name)
    print(
        '            #(.LOC("%s"), .BEL("%s"), .FORCE_CE1(%d), .nFORCE_R0(%d))'
        % (loc, bel, force_ce, force_r))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 4]), .dout(dout[  %d]));'
        % (i, 4 * i, 1 * i))
    f.write('%s,%s,%s,%s\n' % (name, loc, force_ce, force_r))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module clb_FDRE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y114";
    parameter BEL="AFF";
    parameter FORCE_CE1=0;
    parameter nFORCE_R0=1;
    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    FDRE ff (
        .C(clk),
        .Q(dout),
        .CE(din[0] | FORCE_CE1),
        .R(din[1] & nFORCE_R0),
        .D(din[2])
    );
    endmodule
''')
