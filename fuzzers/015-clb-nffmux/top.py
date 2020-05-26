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
        variants = ['AX', 'CY', 'F78', 'O5', 'O6', 'XOR', 'MC31']
    else:
        loc = next(slicels)
        variants = ['AX', 'CY', 'F78', 'O5', 'O6', 'XOR']

    modules = ['clb_NFFMUX_' + x for x in variants]
    module = random.choice(modules)

    if module == 'clb_NFFMUX_MC31':
        n = 3  # Only DOUTMUX has MC31 input
    elif module == 'clb_NFFMUX_F78':
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
        output wire mc31,
        output wire ff_q, //always connect to output
        input wire ff_d); //mux output net
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    parameter ALUT_SRL=0;

    wire [3:0] caro_all;
    assign caro = caro_all[N];
    wire [3:0] carco_all;
    assign carco = carco_all[N];

    wire [3:0] lutno6;
    wire [3:0] lutno5;
    assign bo5 = lutno5[N];
    assign bo6 = lutno6[N];

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
            (* LOC=LOC, BEL="DFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
        if (N == 2) begin
            (* LOC=LOC, BEL="CFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
        if (N == 1) begin
            (* LOC=LOC, BEL="BFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
        if (N == 0) begin
            (* LOC=LOC, BEL="AFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
    endgenerate
endmodule

//******************************************************************************
//BFFMUX tests

module clb_NFFMUX_AX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;

    /*
    D: DX
        drawn a little differently
        not a mux control
        becomes a dedicated external signal
    C: CX
    B: BX
    A: AX
    */
    wire ax = din[6]; //used on MUX8:S, MUX7A:S, and MUX7B:S

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(dout[0]),
            .ff_d(ax));

endmodule

module clb_NFFMUX_CY (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire carco;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(carco),
            .bo5(), .bo6(),
            .ff_q(dout[0]),
            .ff_d(carco));
endmodule

module clb_NFFMUX_F78 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire lut8o, lut7bo, lut7ao;

    /*
    D: N/A (no such mux position)
    C: F7B:O
    B: F8:O
    A: F7A:O
    */
    wire ff_d;

    generate
        if (N == 3) begin
            //No muxes, so this is undefined
           invalid_configuration invalid_configuration3();
        end else if (N == 2) begin
            assign ff_d = lut7bo;
        end else if (N == 1) begin
            assign ff_d = lut8o;
        end else if (N == 0) begin
            assign ff_d = lut7ao;
        end
    endgenerate

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(lut8o), .lut7bo(lut7bo), .lut7ao(lut7ao),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(dout[0]),
            .ff_d(ff_d));
endmodule

module clb_NFFMUX_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire bo5;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(bo5), .bo6(),
            .ff_q(dout[0]),
            .ff_d(bo5));
endmodule

module clb_NFFMUX_O6 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire bo6;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(bo6),
            .ff_q(dout[0]),
            .ff_d(bo6));
endmodule

module clb_NFFMUX_XOR (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire caro;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(caro), .carco(),
            .bo5(), .bo6(bo6),
            .ff_q(dout[0]),
            .ff_d(caro));
endmodule

module clb_NFFMUX_MC31 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1; // Dummy
    wire mc31;

    myLUT8 #(.LOC(LOC), .N(3), .ALUT_SRL(1))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(caro), .carco(),
            .bo5(), .bo6(bo6),
            .mc31(mc31),
            .ff_q(dout[0]),
            .ff_d(mc31));
endmodule
''')
