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
CLBN = 40 + int(INCREMENT)
print('//Requested CLBs: %s' % str(CLBN))


def gen_slices():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEL', 'SLICEM']):
        yield site_name


DIN_N = CLBN * 8
DOUT_N = CLBN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('module,loc,n,def_a\n')
slices = gen_slices()
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    bel = ''

    module = 'clb_N5FFMUX'
    n = random.randint(0, 3)
    def_a = random.randint(0, 1)
    loc = next(slices)

    print('    %s' % module)
    print('            #(.LOC("%s"), .N(%d), .DEF_A(%d))' % (loc, n, def_a))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
        % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s,%s\n' % (module, loc, n, def_a))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module clb_N5FFMUX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=-1;
    parameter DEF_A=1;
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    reg [3:0] ffds;
    wire lutdo5, lutco5, lutbo5, lutao5;
    //wire lutno5 [3:0] = {lutao5, lutbo5, lutco5, lutdo5};
    wire lutno5 [3:0] = {lutdo5, lutco5, lutbo5, lutao5};
    always @(*) begin
        if (DEF_A) begin
            //Default poliarty A
            ffds[3] = lutdo5;
            ffds[2] = lutco5;
            ffds[1] = lutbo5;
            ffds[0] = lutao5;
            ffds[N] = din[6];
        end else begin
            //Default polarity B
            ffds[3] = din[6];
            ffds[2] = din[6];
            ffds[1] = din[6];
            ffds[0] = din[6];
            ffds[N] = lutno5[N];
        end
    end

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

	(* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lutd (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutdo5),
		.O6(lutdo));
	(* LOC=LOC, BEL="D5FF" *)
	FDPE ffd (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[3]));

	(* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutc (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutco5),
		.O6(lutco));
	(* LOC=LOC, BEL="C5FF" *)
	FDPE ffc (
		.C(clk),
		.Q(dout[2]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[2]));

	(* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_CAFE_0000_0001)
	) lutb (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutbo5),
		.O6(lutbo));
	(* LOC=LOC, BEL="B5FF" *)
	FDPE ffb (
		.C(clk),
		.Q(dout[3]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[1]));

	(* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_1CE0_0000_0001)
	) luta (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutao5),
		.O6(lutao));
	(* LOC=LOC, BEL="A5FF" *)
	FDPE ffa (
		.C(clk),
		.Q(dout[4]),
		.CE(din[0]),
		.PRE(din[1]),
		//D can only come from O5 or AX
		//AX is used by MUXF7:S
		.D(ffds[0]));
endmodule
''')
