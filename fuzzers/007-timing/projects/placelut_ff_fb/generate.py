#!/usr/bin/env python
'''
Note: vivado will (by default) fail bitgen DRC on LUT feedback loops
Looks like can probably be disabled, but we actually don't need a bitstream for timing analysis

ERROR: [Vivado 12-2285] Cannot set LOC property of instance 'roi/lut_x22y102_D', Instance roi/lut_x22y102_D can not be placed in D6LUT of site SLICE_X18Y103 because the bel is occupied by roi/lut_x18y103_D(port:). This could be caused by bel constraint conflict
Resolution: When using BEL constraints, ensure the BEL constraints are defined before the LOC constraints to avoid conflicts at a given site.

'''

import argparse
import random

random.seed()

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

print('//placelut w/ FF + feedback')
print('//SBASE: %s' % (SBASE, ))
print('//SDX: %s' % (SDX, ))
print('//SDY: %s' % (SDX, ))
print('//nlut: %s' % (nlut, ))
print(
    '''\
module roi (
        input wire clk,
        input wire [%u:0] ins,
        output wire [%u:0] outs);''') % (nin - 1, nout - 1)

ini = 0
outi = 0
for lutx in xrange(SBASE[0], SBASE[0] + SDX):
    for luty in xrange(SBASE[1], SBASE[1] + SDY):
        loc = "SLICE_X%uY%u" % (lutx, luty)
        for belc in 'ABCD':
            bel = '%c6LUT' % belc
            name = 'lut_x%uy%u_%c' % (lutx, luty, belc)
            print(
                '''\

    (* KEEP, DONT_TOUCH, LOC="%s", BEL="%s" *)
    LUT6 #(
        .INIT(64'hBAD1DEA_1DEADCE0)
    ) %s (''') % (loc, bel, name)
            for i in xrange(6):
                rval = random.randint(0, 9)
                if rval < 3:
                    wfrom = 'ins[%u]' % ini
                    ini += 1
                #elif rval < 6:
                #    wfrom = 'outsr[%u]' % random.randint(0, nout - 1)
                else:
                    wfrom = 'outs[%u]' % random.randint(0, nout - 1)
                print('''\
        .I%u(%s),''' % (i, wfrom))
            out_w = name + '_o'
            print('''\
        .O(%s));''') % (out_w, )

            outs_w = "outs[%u]" % outi
            if random.randint(0, 9) < 5:
                print('    assign %s = %s;' % (outs_w, out_w))
            else:
                out_r = name + '_or'
                print(
                    '''\
    reg %s;
    assign %s = %s;
    always @(posedge clk) begin
        %s = %s;
    end
    ''' % (out_r, outs_w, out_r, out_r, out_w))
            outi += 1

#assert nin == ini
assert nout == outi

print(
    '''
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
