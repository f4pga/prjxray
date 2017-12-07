import random
random.seed(0)
import os
import re

from prims import *

def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for xrange)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(r'SLICE_X(.*)Y(.*):SLICE_X(.*)Y(.*)', os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))

CLBN = 600
SLICEX, SLICEY = slice_xy()
# 800
SLICEN = (SLICEY[1] - SLICEY[0]) * (SLICEX[1] - SLICEX[0])
print('//SLICEX: %s' % str(SLICEX))
print('//SLICEY: %s' % str(SLICEY))
print('//SLICEN: %s' % str(SLICEN))
print('//Requested CLBs: %s' % str(CLBN))

f = open("top.txt", "w")
f.write("i,prim,loc,bel,init\n")

def gen_slices():
    for slicey in range(*SLICEY):
        for slicex in range(*SLICEX):
            yield "SLICE_X%dY%d" % (slicex, slicey)

DIN_N = CLBN * 4
DOUT_N = CLBN * 1

print('''
module top(input clk, stb, di, output do);
	localparam integer DIN_N = %d;
	localparam integer DOUT_N = %d;

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

	roi roi (
		.clk(clk),
		.din(din),
		.dout(dout)
	);
endmodule
''' % (DIN_N, DOUT_N))

slices = gen_slices()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    ffprim = random.choice(ones(ffprims))
    # clb_FD clb_FD (.clk(clk), .din(din[  0 +: 4]), .dout(dout[  0]));
    # clb_FD_1 clb_FD_1 (.clk(clk), .din(din[  4 +: 4]), .dout(dout[  1]));
    loc = next(slices)
    # Latch can't go in 5s
    if isff(ffprim):
        bel = random.choice(ff_bels)
    else:
        bel = random.choice(ff_bels_ffl)
    init = random.choice((0, 1))
    #bel = "AFF"
    print('    clb_%s' % ffprim)
    print('            #(.LOC("%s"), .BEL("%s"), .INIT(%d))' % (loc, bel, init))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 4]), .dout(dout[  %d]));' % (i, 4 * i, 1 * i))
    f.write("%d,%s,%s,%s,%d\n" % (i, ffprim, loc, bel, init))
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module clb_FD (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y100";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FD ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
	endmodule

module clb_FD_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y101";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FD_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
	endmodule

module clb_FDC (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y102";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDC ff (
		.C(clk),
		.Q(dout),
		.CLR(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDC_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y103";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDC_1 ff (
		.C(clk),
		.Q(dout),
		.CLR(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDCE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y104";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDCE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDCE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y105";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDCE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y106";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDE ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.CE(din[1])
	);
	endmodule

module clb_FDE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y107";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDE_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.CE(din[1])
	);
	endmodule

module clb_FDP (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y108";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDP ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_FDP_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y109";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDP_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_FDPE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y110";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDPE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDPE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y111";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDPE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDR (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y112";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDR ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.R(din[1])
	);
	endmodule

module clb_FDR_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y113";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDR_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.R(din[1])
	);
	endmodule

module clb_FDRE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y114";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDRE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDRE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y115";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDRE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDS (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y116";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDS ff (
		.C(clk),
		.Q(dout),
		.S(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDS_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y117";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDS_1 ff (
		.C(clk),
		.Q(dout),
		.S(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDSE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y118";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDSE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDSE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y119";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	FDSE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	endmodule

//********************************************************************************

module clb_LDC (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y120";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDC ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.CLR(din[1])
	);
	endmodule
module clb_LDC_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y121";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDC_1 ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.CLR(din[1])
	);
	endmodule

module clb_LDCE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y122";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDCE ff (
		.G(~clk),
		//NOTE: diagram shows two outputs. Error?
		.Q(dout),
		.D(din[0]),
		.GE(din[1]),
		.CLR(din[2])
	);
	endmodule
module clb_LDCE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y123";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDCE_1 ff (
		.G(~clk),
		//NOTE: diagram shows two outputs. Error?
		.Q(dout),
		.D(din[0]),
		.GE(din[1]),
		.CLR(din[2])
	);
	endmodule

module clb_LDE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y124";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDE ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.GE(din[1])
	);
	endmodule
module clb_LDE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y125";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDE_1 ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.GE(din[1])
	);
	endmodule

module clb_LDP (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y126";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDP ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule
module clb_LDP_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y127";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDP_1 ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_LDPE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y128";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDPE ff (
		.G(~clk),
		.Q(dout),
		.PRE(din[0]),
		.D(din[1]),
		.GE(din[2])
	);
	endmodule
module clb_LDPE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y129";
    parameter BEL="AFF";
    parameter INIT=1'b0;
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)
	LDPE_1 ff (
		.G(~clk),
		.Q(dout),
		.PRE(din[0]),
		.D(din[1]),
		.GE(din[2])
	);
	endmodule

''')

