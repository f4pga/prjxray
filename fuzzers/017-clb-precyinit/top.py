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
from prjxray import verilog
from prjxray import util

# INCREMENT is the amount of additional CLBN to be instantiated in the design.
# This makes the fuzzer compilation more robust against failures.
INCREMENT = os.getenv('CLBN', 0)
CLBN = 400 + int(INCREMENT)
SLICEX, SLICEY = util.site_xy_minmax([
    'SLICEL',
    'SLICEM',
])
# 800
SLICEN = (SLICEY[1] - SLICEY[0]) * (SLICEX[1] - SLICEX[0])
print('//SLICEX: %s' % str(SLICEX))
print('//SLICEY: %s' % str(SLICEY))
print('//SLICEN: %s' % str(SLICEN))
print('//Requested CLBs: %s' % str(CLBN))


# Rearranged to sweep Y so that carry logic is easy to allocate
# XXX: careful...if odd number of Y in ROI will break carry
def gen_slices():
    for slicex in range(*SLICEX):
        for slicey in range(*SLICEY):
            # caller may reject position if needs more room
            yield ("SLICE_X%dY%d" % (slicex, slicey), (slicex, slicey))


DIN_N = CLBN * 8
DOUT_N = CLBN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('module,loc,loc2\n')
slices = gen_slices()
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    # Don't have an O6 example
    modules = ['clb_PRECYINIT_' + x for x in ['0', '1', 'AX', 'CIN']]
    loc, loc_pos = next(slices)
    while True:
        module = random.choice(modules)

        if module == 'clb_PRECYINIT_CIN':
            # Need at least extra Y for CIN extra CLB
            if loc_pos[1] >= SLICEY[1] - 1:
                continue
            loc_co = loc
            loc_ci, _pos_ci = next(slices)
            params = '.LOC_CO("%s"), .LOC_CI("%s")' % (loc_co, loc_ci)
            # Don't really care about co, but add for completeness
            paramsc = loc_ci + ',' + loc_co
        else:
            params = '.LOC("%s")' % loc
            paramsc = loc + ',' + ''
        break

    print('    %s' % module)
    print('            #(%s)' % (params))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
        % (i, 8 * i, 8 * i))

    f.write('%s,%s\n' % (module, paramsc))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module clb_PRECYINIT_0 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(1'b0), .CI());
endmodule

module clb_PRECYINIT_1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(1'b1), .CI());
endmodule

module clb_PRECYINIT_AX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[0]), .CI());
endmodule

module clb_PRECYINIT_CIN (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC_CO="SLICE_FIXME";
    parameter LOC_CI="SLICE_FIXME";

    wire [3:0] co;

    //Gets CI
	(* LOC=LOC_CI, KEEP, DONT_TOUCH *)
    CARRY4 carry4_co(.O(), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(co[3]), .CI());
    //Sends CO
	(* LOC=LOC_CO, KEEP, DONT_TOUCH *)
    CARRY4 carry4_ci(.O(), .CO(co), .DI(din[3:0]), .S(din[7:4]), .CYINIT(1'b0), .CI());
endmodule
''')
