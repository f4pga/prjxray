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
CLBN = 600 + int(INCREMENT)
print('//Requested CLBs: %s' % str(CLBN))


def gen_slicels():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEL']):
        yield site_name


def gen_slicems():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEM']):
        yield site_name


DIN_N = CLBN * 8
DOUT_N = CLBN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('module,loc,n\n')
slicels = gen_slicels()
slicems = gen_slicems()
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):

    use_slicem = (i % 2) == 0

    if use_slicem:
        loc = next(slicems)
        variants = ['CY', 'F78', 'O5', 'XOR', 'B5Q', 'MC31']
    else:
        loc = next(slicels)
        variants = ['CY', 'F78', 'O5', 'XOR', 'B5Q']

    # Don't have an O6 example
    modules = ['clb_NOUTMUX_' + x for x in variants]
    module = random.choice(modules)

    if module == 'clb_NOUTMUX_MC31':
        n = 3  # Only DOUTMUX has MC31 input
    elif module == 'clb_NOUTMUX_F78':
        n = random.randint(0, 2)
    else:
        n = random.randint(0, 3)

    print('    %s' % module)
    print('            #(.LOC("%s"), .N(%d))' % (loc, n))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
        % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s\n' % (module, loc, n))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module myLUT8 (input clk, input [7:0] din,
        output lut8o, output lut7bo, output lut7ao,
        //caro: XOR additional result (main output)
        //carco: CLA result (carry module additional output)
        output caro, output carco,
        output bo5, output bo6,
        //Note: b5ff_q requires the mux and will conflict with other wires
        //Otherwise this FF drops out
        //output wire [3:0] n5ff_q);
        output wire ff_q,
        output wire mc31);

    parameter N=-1;
    parameter LOC="SLICE_FIXME";
    parameter ALUT_SRL=0;

    wire [3:0] caro_all;
    assign caro = caro_all[N];
    wire [3:0] carco_all;
    assign carco = carco_all[N];

    wire [3:0] lutno6;
    assign bo6 = lutno6[N];
    wire [3:0] lutno5;
    assign bo5 = lutno5[N];

    //Outputs does not have to be used, will stay without it
    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(lut8o), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutno6[3]), .I1(lutno6[2]), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutno6[1]), .I1(lutno6[0]), .S(din[6]));

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
		.O5(lutno5[3]),
		.O6(lutno6[3]));

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
		.O5(lutno5[2]),
		.O6(lutno6[2]));

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
		.O5(lutno5[1]),
		.O6(lutno6[1]));

    generate if (ALUT_SRL != 0) begin

    (* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
	SRLC32E #(
		.INIT(64'h8000_1CE0_0000_0001)
	) srla (
        .CLK(clk),
        .CE(din[6]),
        .D(din[5]),
		.A(din[4:0]),
		.Q(lutno6[0]),
        .Q31(mc31));

    assign lutno5[0] = din[6];

    end else begin

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
		.O5(lutno5[0]),
		.O6(lutno6[0]));

    end endgenerate

    //Outputs do not have to be used, will stay without them
	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(caro_all), .CO(carco_all), .DI(lutno5), .S(lutno6), .CYINIT(1'b0), .CI());

    generate
        if (N == 3) begin
	        (* LOC=LOC, BEL="D5FF", KEEP, DONT_TOUCH *)
	        FDPE d5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[3]));
        end
        if (N == 2) begin
	        (* LOC=LOC, BEL="C5FF", KEEP, DONT_TOUCH *)
	        FDPE c5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[2]));
        end
        if (N == 1) begin
	        (* LOC=LOC, BEL="B5FF", KEEP, DONT_TOUCH *)
	        FDPE b5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[1]));
        end
        if (N == 0) begin
	        (* LOC=LOC, BEL="A5FF", KEEP, DONT_TOUCH *)
	        FDPE a5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[0]));
        end
    endgenerate
endmodule

//******************************************************************************
//BOUTMUX tests

module clb_NOUTMUX_CY (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(),
            .caro(), .carco(dout[0]),
            .bo5(), .bo6(),
            .ff_q());
endmodule

//clb_NOUTMUX_F78: already have above as clb_LUT8
module clb_NOUTMUX_F78 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;
    wire lut8o, lut7bo, lut7ao;
    /*
    D: N/A (no such mux position)
    C: F7B:O
    B: F8:O
    A: F7A:O
    */
    generate
        if (N == 3) begin
            //No muxes, so this is undefined
           invalid_configuration invalid_configuration3();
        end else if (N == 2) begin
            assign dout[0] = lut7bo;
        end else if (N == 1) begin
            assign dout[0] = lut8o;
        end else if (N == 0) begin
            assign dout[0] = lut7ao;
        end
    endgenerate

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(lut8o), .lut7bo(lut7bo), .lut7ao(lut7ao),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q());
endmodule

module clb_NOUTMUX_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(),
            .caro(), .carco(),
            .bo5(dout[0]), .bo6(),
            .ff_q());
endmodule

/*
//FIXME: need to force it to use both X and O6
module clb_NOUTMUX_O6 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(), .co(), .carco(), .bo5(), .bo6());
endmodule
*/

module clb_NOUTMUX_XOR (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(),
            .caro(dout[0]), .carco(),
            .bo5(), .bo6(),
            .ff_q());
endmodule

module clb_NOUTMUX_B5Q (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(dout[0]));
endmodule

module clb_NOUTMUX_MC31 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=0; // Dummy

    myLUT8 #(.LOC(LOC), .N(0), .ALUT_SRL(1))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(), .mc31(dout[0]));
endmodule
''')
