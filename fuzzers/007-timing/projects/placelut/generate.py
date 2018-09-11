#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--sdx', default='8', help='')
parser.add_argument('--sdy', default='4', help='')
args = parser.parse_args()

'''
Generate in pairs
Fill up switchbox quad for now
Create random connections between the LUTs
See how much routing pressure we can generate

Start with non-random connections to the LFSR for solver comparison

Start at SLICE_X16Y102
'''
SBASE = (16, 102)
SDX = int(args.sdx, 0)
SDY = int(args.sdy, 0)
nlut = 4 * SDX * SDY

nin = 6 * nlut
nout = nlut

print('//placelut simple')
print('//SBASE: %s' % (SBASE,))
print('//SDX: %s' % (SDX,))
print('//SDY: %s' % (SDX,))
print('//nlut: %s' % (nlut,))
print('''\
module roi (
        input wire clk,
        input wire [%u:0] ins,
        output wire [%u:0] outs);''') % (nin - 1, nout -1)

ini = 0
outi = 0
for lutx in xrange(SBASE[0], SBASE[0] + SDX):
    for luty in xrange(SBASE[1], SBASE[1] + SDY):
        loc = "SLICE_X%uY%u" % (lutx, luty)
        for belc in 'ABCD':
            bel = '%c6LUT' % belc
            print('''\

	(* KEEP, DONT_TOUCH, LOC="%s", BEL="%s" *)
	LUT6 #(
		.INIT(64'hBAD1DEA_1DEADCE0)
	) %s (''') % (loc, bel, 'lut_x%uy%u_%c' % (lutx, luty, belc))
            for i in xrange(6):
                print('''\
		.I%u(ins[%u]),''' % (i, ini))
                ini += 1
            print('''\
		.O(outs[%u]));''') % (outi,)
            outi += 1
assert nin == ini
assert nout == outi

print('''
endmodule

module top(input wire clk, input wire stb, input wire di, output wire do);
    localparam integer DIN_N = %u;
    localparam integer DOUT_N = %u;

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
    roi roi(
            .clk(clk),
            .ins(din),
            .outs(dout)
            );
endmodule''') % (nin, nout)

