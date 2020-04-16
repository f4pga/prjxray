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
import os, random
random.seed(0)
from prjxray import util
from prjxray import verilog

# INCREMENT is the amount of additional CLBN to be instantiated in the design.
# This makes the fuzzer compilation more robust against failures.
INCREMENT = os.getenv('CLBN', 0)
CLBN = 400 + int(INCREMENT)
print('//Requested CLBs: %s' % str(CLBN))


def gen_slices():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEL', 'SLICEM']):
        yield site_name


DIN_N = CLBN * 8
DOUT_N = CLBN * 8

lut_bels = ['A6LUT', 'B6LUT', 'C6LUT', 'D6LUT']

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('module,loc,bel,n\n')
slices = gen_slices()
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    bel = ''

    if random.randint(0, 1):
        module = 'clb_NCY0_MX'
    else:
        module = 'clb_NCY0_O5'
    n = random.randint(0, 3)
    loc = next(slices)
    bel = lut_bels[n]

    print('    %s' % module)
    print('            #(.LOC("%s"), .BEL("%s"), .N(%d))' % (loc, bel, n))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
        % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s,%s\n' % (module, loc, bel, n))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module clb_NCY0_MX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X16Y129_FIXME";
    parameter BEL="A6LUT_FIXME";
    parameter N=-1;

    wire [3:0] o;
    wire o6, o5;
    reg [3:0] s;

    always @(*) begin
        s = din[7:4];
        s[N] = o6;
    end

	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(o5),
		.O6(o6));

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(s), .CYINIT(1'b0), .CI());

	(* LOC=LOC, BEL=\"AFF\", KEEP, DONT_TOUCH *)
    FDRE fdce1(.D(o[0]), .C(clk), .CE(), .R(), .Q());
	(* LOC=LOC, BEL=\"BFF\", KEEP, DONT_TOUCH *)
    FDRE fdce2(.D(o[1]), .C(clk), .CE(), .R(), .Q());
	(* LOC=LOC, BEL=\"CFF\", KEEP, DONT_TOUCH *)
    FDRE fdce3(.D(o[2]), .C(clk), .CE(), .R(), .Q());
	(* LOC=LOC, BEL=\"DFF\", KEEP, DONT_TOUCH *)
    FDRE fdce4(.D(o[3]), .C(clk), .CE(), .R(), .Q());
endmodule

module clb_NCY0_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X16Y129_FIXME";
    parameter BEL="A6LUT_FIXME";
    parameter N=-1;

    wire [3:0] o;
    wire o6, o5;
    reg [3:0] s;
    reg [3:0] di;

    always @(*) begin
        s = din[7:4];
        s[N] = o6;

        di = {din[3:0]};
        di[N] = o5;
    end

	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(o5),
		.O6(o6));

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(di), .S(s), .CYINIT(1'b0), .CI());

	(* LOC=LOC, BEL=\"AFF\", KEEP, DONT_TOUCH *)
    FDRE fdce1(.D(o[0]), .C(clk), .CE(), .R(), .Q());
	(* LOC=LOC, BEL=\"BFF\", KEEP, DONT_TOUCH *)
    FDRE fdce2(.D(o[1]), .C(clk), .CE(), .R(), .Q());
	(* LOC=LOC, BEL=\"CFF\", KEEP, DONT_TOUCH *)
    FDRE fdce3(.D(o[2]), .C(clk), .CE(), .R(), .Q());
	(* LOC=LOC, BEL=\"DFF\", KEEP, DONT_TOUCH *)
    FDRE fdce4(.D(o[3]), .C(clk), .CE(), .R(), .Q());
endmodule
''')
