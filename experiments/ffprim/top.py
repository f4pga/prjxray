import random

random.seed(0)

CLBN = 600
# SLICE_X12Y100
# SLICE_X27Y149
SLICEX = (12, 28)
SLICEY = (100, 150)
# 800
SLICEN = (SLICEY[1] - SLICEY[0]) * (SLICEX[1] - SLICEX[0])
print('//SLICEX: %s' % str(SLICEX))
print('//SLICEY: %s' % str(SLICEY))
print('//SLICEN: %s' % str(SLICEN))
print('//Requested CLBs: %s' % str(CLBN))

def gen_slices():
    for slicey in range(*SLICEY):
        for slicex in range(*SLICEX):
            yield "SLICE_X%dY%d" % (slicex, slicey)

DIN_N = CLBN * 4
DOUT_N = CLBN * 1
ffprims = (
        'FD',
        'FD_1',
        'FDC',
        'FDC_1',
        'FDCE',
        'FDCE_1',
        'FDE',
        'FDE_1',
        'FDP',
        'FDP_1',
        'FDPE',
        'FDPE_1',
        'FDR',
        'FDR_1',
        'FDRE',
        'FDRE_1',
        'FDS',
        'FDS_1',
        'FDSE',
        'FDSE_1',
        )
ffprims = (
        'FDRE',
        'FDSE',
        'FDCE',
        'FDPE',
)
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
    ffprim = random.choice(ffprims)
    # clb_FD clb_FD (.clk(clk), .din(din[  0 +: 4]), .dout(dout[  0]));
    # clb_FD_1 clb_FD_1 (.clk(clk), .din(din[  4 +: 4]), .dout(dout[  1]));
    loc = next(slices)
    #bel = random.choice(ff_bels)
    bel = "AFF"
    print('    clb_%s' % ffprim)
    print('            #(.LOC("%s"), .BEL("%s"))' % (loc, bel))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 4]), .dout(dout[  %d]));' % (i, 4 * i, 1 * i))
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module clb_FD (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y100";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	FD ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
	endmodule

module clb_FD_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y101";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	FD_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
	endmodule

module clb_FDC (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y102";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	FDSE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	endmodule
''')

