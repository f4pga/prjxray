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
'''
Need coverage for the following:
RAM32X1S_N
RAM32X1D
RAM32M
RAM64X1S_N
RAM64X1D_N
RAM64M
RAM128X1S_N
RAM128X1D
RAM256X1S
SRL16E_N
SRLC32E_N

Note: LUT6 was added to try to simplify reduction, although it might not be needed
'''

import os, random
random.seed(0)
from prjxray import util
from prjxray import verilog

# INCREMENT is the amount of additional CLBN to be instantiated in the design.
# This makes the fuzzer compilation more robust against failures.
INCREMENT = os.getenv('CLBN', 0)
CLBN = 50 + int(INCREMENT)
print('//Requested CLBs: %s' % str(CLBN))


def gen_slicems():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEM']):
        yield site_name


DIN_N = CLBN * 8
DOUT_N = CLBN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('module,loc,bela,belb,belc,beld\n')
slices = sorted(gen_slicems())
random.shuffle(slices)

print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
randluts = 0
for clbi, loc in zip(range(CLBN), slices):
    params = ''
    cparams = ''
    # Multi module
    # Fill with random assortment of SRL16E and SRLC32E
    if random.randint(0, 1):
        params = ''
        module = 'my_ram_N'

        # Can fit 4 per CLB
        # BELable
        bel_opts = [
            'SRL16E',
            'SRLC32E',
            # Weight LUT6 more heavily to make WEMUX.CE solve quicker
            'LUT6',
            'LUT6',
        ]

        bels = []
        for beli in range(4):
            belc = chr(ord('A') + beli)
            if randluts:
                bel = random.choice(bel_opts)
            else:
                # Force one without memory elements to bring CE bit low
                bel = 'LUT6'

            params += ', .%c_%s(1)' % (belc, bel)
            bels.append(bel)
        # Record the BELs we chose in the module (A, B, C, D)
        cparams = ',' + (','.join(bels))
        randluts += 1
    # Greedy module
    # Don't place anything else in it
    # For solving muxes vs previous results
    else:
        modules = [
            # (module,          N max, FF opt)
            ('my_RAM32X1S_N', 4, 0),
            ('my_RAM32X1D', None, 0),
            ('my_RAM32M', None, 0),
            ('my_RAM64X1S_N', 4, 0),
            ('my_RAM64X1D_N', 2, 0),
            ('my_RAM64M', None, 0),
            ('my_RAM128X1S_N', 2, 1),
            ('my_RAM128X1D', None, 1),
            ('my_RAM256X1S', None, 1),
        ]

        module, nmax, ff_param = random.choice(modules)

        n = ''
        if nmax:
            n = random.randint(1, nmax)
            params += ',.N(%d)' % n
        cparams += ',%s' % n

        ff = ''
        if ff_param:
            ff = random.randint(0, 1)
            params += ',.FF(%d)' % ff
        cparams += ',%s' % ff

        # Pad to match above CSV size
        cparams += ",,"

    print('    %s' % module)
    print('            #(.LOC("%s")%s)' % (loc, params))
    sel = random.random()
    if sel > .15:
        print(
            '            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
            % (clbi, 8 * clbi, 8 * clbi))
    else:
        print(
            "            clb_%d (.clk(clk), .din({8{1'b1}}), .dout());" %
            (clbi, ))

    f.write('%s,%s%s\n' % (module, loc, cparams))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''

//***************************************************************
//Basic

module maybe_ff (input clk, din, dout);
    parameter FF = 0;

    generate
        if (FF) begin
            reg r;
            assign dout = r;
            always @(posedge clk) begin
                r = din;
            end
        end else begin
            assign dout = din;
        end
    endgenerate
endmodule

module my_RAM32X1S_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    //1-4
    parameter N=1;

    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : loop
            (* LOC=LOC, KEEP, DONT_TOUCH *)
            RAM32X1S #(
                ) RAM32X1S (
                    .O(dout[i]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .A4(din[4]),
                    .D(din[5]),
                    .WCLK(clk),
                    .WE(ce));
        end
    endgenerate
endmodule

module my_RAM32X1D (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM32X1D #(
        ) RAM32X1D (
            .DPO(dout[0]),
            .SPO(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .DPRA0(din[6]),
            .DPRA1(din[7]),
            .DPRA2(din[0]),
            .DPRA3(din[1]),
            .DPRA4(din[2]),
            .WCLK(din[3]),
            .WE(din[4]));
endmodule

module my_RAM32M (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM32M #(
        ) RAM32M (
            .DOA(dout[1:0]),
            .DOB(dout[3:2]),
            .DOC(dout[5:4]),
            .DOD(dout[7:6]),
            .ADDRA(din[4:0]),
            .ADDRB(din[4:0]),
            .ADDRC(din[4:0]),
            .ADDRD(din[4:0]),
            .DIA(din[5:4]),
            .DIB(din[6:5]),
            .DIC(din[7:6]),
            .DID(din[1:0]),
            .WCLK(din[1]),
            .WE(din[2]));
endmodule

module my_RAM64X1S_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    //1-4
    parameter N=1;

    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : loop
            (* LOC=LOC, KEEP, DONT_TOUCH *)
            RAM64X1S #(
                ) RAM64X1S (
                    .O(dout[i]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .A4(din[4]),
                    .A5(din[5]),
                    .D(din[6]),
                    .WCLK(clk),
                    .WE(ce));
        end
    endgenerate
endmodule

module my_RAM64X1D_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    //1-2
    parameter N=1;

    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : loop
            (* LOC=LOC, KEEP, DONT_TOUCH *)
            RAM64X1D #(
                    .INIT(64'h0),
                    .IS_WCLK_INVERTED(1'b0)
                ) ramb (
                    .DPO(dout[i]),
                    .D(din[0]),
                    .WCLK(clk),
                    .WE(din[2]),
                    .A0(din[3]),
                    .A1(din[4]),
                    .A2(din[5]),
                    .A3(din[6]),
                    .A4(din[7]),
                    .A5(din[0]),
                    .DPRA0(din[1]),
                    .DPRA1(din[2]),
                    .DPRA2(din[3]),
                    .DPRA3(din[4]),
                    .DPRA4(din[5]),
                    .DPRA5(din[6]));
        end
    endgenerate
endmodule

module my_RAM64M (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    RAM64M #(
        ) RAM64M (
            .DOA(dout[0]),
            .DOB(dout[1]),
            .DOC(dout[2]),
            .DOD(dout[3]),
            .ADDRA(din[0]),
            .ADDRB(din[1]),
            .ADDRC(din[2]),
            .ADDRD(din[3]),
            .DIA(din[4]),
            .DIB(din[5]),
            .DIC(din[6]),
            .DID(din[7]),
            .WCLK(clk),
            .WE(din[1]));
endmodule

module my_RAM128X1S_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    //1-2
    parameter N=1;
    parameter FF = 0;

    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : loop
            wire o;

            (* LOC=LOC, KEEP, DONT_TOUCH *)
            RAM128X1S #(
                ) RAM128X1S (
                    .O(o),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .A4(din[4]),
                    .A5(din[5]),
                    .A6(din[6]),
                    .D(din[7]),
                    .WCLK(din[0]),
                    .WE(din[1]));

            maybe_ff #(.FF(FF)) ff (.clk(clk), .din(o), .dout(dout[i]));
        end
    endgenerate
endmodule

module my_RAM128X1D (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter FF = 0;

    wire dpo, spo;

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1D #(
            .INIT(128'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) RAM128X1D (
            .DPO(dpo),
            .SPO(spo),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]));

    maybe_ff #(.FF(FF)) ff0 (.clk(clk), .din(dpo), .dout(dout[0]));
    maybe_ff #(.FF(FF)) ff1 (.clk(clk), .din(spo), .dout(dout[1]));
endmodule

//Dedicated LOC
module my_RAM256X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter FF = 0;

    wire o;

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM256X1S #(
        ) RAM256X1S (
            .O(o),
            .A({din[0], din[7:0]}),
            .D(din[0]),
            .WCLK(din[1]),
            .WE(din[2]));

    maybe_ff #(.FF(FF)) ff (.clk(clk), .din(o), .dout(dout[0]));
endmodule

//***************************************************************

module my_ram_N_inst (input clk, input [7:0] din, output dout);
    parameter LOC="";
    parameter BEL="";
    parameter N_SRL16E=0;
    parameter N_SRLC32E=0;
    parameter N_LUT6=0;

    parameter SRLINIT = 32'h00000000;
    parameter LUTINIT6 = 64'h0000_0000_0000_0000;

    wire ce = din[4];

    generate
        //********************
        if (N_SRL16E) begin
            (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
            SRL16E #(
                ) lut (
                    .Q(dout),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[6]));
        end
        if (N_SRLC32E) begin
            (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
            SRLC32E #(
                    .INIT(SRLINIT),
                    .IS_CLK_INVERTED(1'b0)
                ) lut (
                    .Q(dout),
                    .Q31(),
                    .A(din[4:0]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[7]));
        end
        if (N_LUT6) begin
	        (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	        LUT6_2 #(
		        .INIT(LUTINIT6)
	        ) lut (
		        .I0(din[0]),
		        .I1(din[1]),
		        .I2(din[2]),
		        .I3(din[3]),
		        .I4(din[4]),
		        .I5(din[5]),
		        .O5(),
		        .O6(dout));
        end
    endgenerate
endmodule

/*
Supermodule for LOC'able prims
Mix and match as needed
Specify at most one function generator per LUT
*/
module my_ram_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter D_SRL16E=0;
    parameter D_SRLC32E=0;
    parameter D_LUT6=0;

    parameter C_SRL16E=0;
    parameter C_SRLC32E=0;
    parameter C_LUT6=0;

    parameter B_SRL16E=0;
    parameter B_SRLC32E=0;
    parameter B_LUT6=0;

    parameter A_SRL16E=0;
    parameter A_SRLC32E=0;
    parameter A_LUT6=0;

    my_ram_N_inst #(.LOC(LOC), .BEL("D6LUT"), .N_SRL16E(D_SRL16E), .N_SRLC32E(D_SRLC32E), .N_LUT6(D_LUT6))
            lutd(.clk(clk), .din(din), .dout(dout[3]));
    my_ram_N_inst #(.LOC(LOC), .BEL("C6LUT"), .N_SRL16E(C_SRL16E), .N_SRLC32E(C_SRLC32E), .N_LUT6(C_LUT6))
            lutc(.clk(clk), .din(din), .dout(dout[2]));
    my_ram_N_inst #(.LOC(LOC), .BEL("B6LUT"), .N_SRL16E(B_SRL16E), .N_SRLC32E(B_SRLC32E), .N_LUT6(B_LUT6))
            lutb(.clk(clk), .din(din), .dout(dout[1]));
    my_ram_N_inst #(.LOC(LOC), .BEL("A6LUT"), .N_SRL16E(A_SRL16E), .N_SRLC32E(A_SRLC32E), .N_LUT6(A_LUT6))
            luta(.clk(clk), .din(din), .dout(dout[0]));
endmodule

''')
