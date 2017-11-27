//https://www.xilinx.com/support/documentation/sw_manuals/xilinx14_1/7series_scm.pdf
//Places one of every FF primitive

/*
LDC => LDCE
LDE => LDCE
LDP => LDPE
*/

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 120;
	localparam integer DOUT_N = 30;

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

module roi(input clk, input [119:0] din, output [29:0] dout);
    /*
    clbs = (
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

            'LDC',
            'LDC_1',
            'LDCE',
            'LDCE_1',
            'LDE',
            'LDE_1',
            'LDPE',
            'LDPE_1',
            'LDP',
            'LDP_1',
            )
    for i, clb in enumerate(clbs):
        print 'clb_%s clb_%s (.clk(clk), .din(din[  %d +: 4]), .dout(dout[  %d ]));' % (clb, clb, i * 4, i * 1)
    */
    //FD
    clb_FD clb_FD (.clk(clk), .din(din[  0 +: 4]), .dout(dout[  0]));
    clb_FD_1 clb_FD_1 (.clk(clk), .din(din[  4 +: 4]), .dout(dout[  1]));
    clb_FDC clb_FDC (.clk(clk), .din(din[  8 +: 4]), .dout(dout[  2]));
    clb_FDC_1 clb_FDC_1 (.clk(clk), .din(din[  12 +: 4]), .dout(dout[  3]));
    clb_FDCE clb_FDCE (.clk(clk), .din(din[  16 +: 4]), .dout(dout[  4]));
    clb_FDCE_1 clb_FDCE_1 (.clk(clk), .din(din[  20 +: 4]), .dout(dout[  5]));
    clb_FDE clb_FDE (.clk(clk), .din(din[  24 +: 4]), .dout(dout[  6]));
    clb_FDE_1 clb_FDE_1 (.clk(clk), .din(din[  28 +: 4]), .dout(dout[  7]));
    clb_FDP clb_FDP (.clk(clk), .din(din[  32 +: 4]), .dout(dout[  8]));
    clb_FDP_1 clb_FDP_1 (.clk(clk), .din(din[  36 +: 4]), .dout(dout[  9]));
    clb_FDPE clb_FDPE (.clk(clk), .din(din[  40 +: 4]), .dout(dout[  10]));
    clb_FDPE_1 clb_FDPE_1 (.clk(clk), .din(din[  44 +: 4]), .dout(dout[  11]));
    clb_FDR clb_FDR (.clk(clk), .din(din[  48 +: 4]), .dout(dout[  12]));
    clb_FDR_1 clb_FDR_1 (.clk(clk), .din(din[  52 +: 4]), .dout(dout[  13]));
    clb_FDRE clb_FDRE (.clk(clk), .din(din[  56 +: 4]), .dout(dout[  14]));
    clb_FDRE_1 clb_FDRE_1 (.clk(clk), .din(din[  60 +: 4]), .dout(dout[  15]));
    clb_FDS clb_FDS (.clk(clk), .din(din[  64 +: 4]), .dout(dout[  16]));
    clb_FDS_1 clb_FDS_1 (.clk(clk), .din(din[  68 +: 4]), .dout(dout[  17]));
    clb_FDSE clb_FDSE (.clk(clk), .din(din[  72 +: 4]), .dout(dout[  18]));
    clb_FDSE_1 clb_FDSE_1 (.clk(clk), .din(din[  76 +: 4]), .dout(dout[  19]));
    //LD
    clb_LDC clb_LDC (.clk(clk), .din(din[  80 +: 4]), .dout(dout[  20 ]));
    clb_LDC_1 clb_LDC_1 (.clk(clk), .din(din[  84 +: 4]), .dout(dout[  21 ]));
    clb_LDCE clb_LDCE (.clk(clk), .din(din[  88 +: 4]), .dout(dout[  22 ]));
    clb_LDCE_1 clb_LDCE_1 (.clk(clk), .din(din[  92 +: 4]), .dout(dout[  23 ]));
    clb_LDE clb_LDE (.clk(clk), .din(din[  96 +: 4]), .dout(dout[  24 ]));
    clb_LDE_1 clb_LDE_1 (.clk(clk), .din(din[  100 +: 4]), .dout(dout[  25 ]));
    clb_LDPE clb_LDPE (.clk(clk), .din(din[  104 +: 4]), .dout(dout[  26 ]));
    clb_LDPE_1 clb_LDPE_1 (.clk(clk), .din(din[  108 +: 4]), .dout(dout[  27 ]));
    clb_LDP clb_LDP (.clk(clk), .din(din[  112 +: 4]), .dout(dout[  28 ]));
    clb_LDP_1 clb_LDP_1 (.clk(clk), .din(din[  116 +: 4]), .dout(dout[  29 ]));
endmodule

// ---------------------------------------------------------------------

module clb_FD (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y100", BEL="AFF" *)
	FD ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
	endmodule
module clb_FD_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y101", BEL="AFF" *)
	FD_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
	endmodule

module clb_FDC (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y102", BEL="AFF" *)
	FDC ff (
		.C(clk),
		.Q(dout),
		.CLR(din[0]),
		.D(din[1])
	);
	endmodule
module clb_FDC_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y103", BEL="AFF" *)
	FDC_1 ff (
		.C(clk),
		.Q(dout),
		.CLR(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDCE (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y104", BEL="AFF" *)
	FDCE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
	endmodule
module clb_FDCE_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y105", BEL="AFF" *)
	FDCE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDE (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y106", BEL="AFF" *)
	FDE ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.CE(din[1])
	);
	endmodule
module clb_FDE_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y107", BEL="AFF" *)
	FDE_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.CE(din[1])
	);
	endmodule

module clb_FDP (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y108", BEL="AFF" *)
	FDP ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule
module clb_FDP_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y109", BEL="AFF" *)
	FDP_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_FDPE (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y110", BEL="AFF" *)
	FDPE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	endmodule
module clb_FDPE_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y111", BEL="AFF" *)
	FDPE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDR (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y112", BEL="AFF" *)
	FDR ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.R(din[1])
	);
	endmodule
module clb_FDR_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y113", BEL="AFF" *)
	FDR_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.R(din[1])
	);
	endmodule

module clb_FDRE (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y114", BEL="AFF" *)
	FDRE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	endmodule
module clb_FDRE_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y115", BEL="AFF" *)
	FDRE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDS (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y116", BEL="AFF" *)
	FDS ff (
		.C(clk),
		.Q(dout),
		.S(din[0]),
		.D(din[1])
	);
	endmodule
module clb_FDS_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y117", BEL="AFF" *)
	FDS_1 ff (
		.C(clk),
		.Q(dout),
		.S(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDSE (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y118", BEL="AFF" *)
	FDSE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	endmodule
module clb_FDSE_1 (input clk, input [3:0] din, output dout);
	(* LOC="SLICE_X16Y119", BEL="AFF" *)
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDC ff (
		.G(clk),
		.Q(dout),
		.D(din[0]),
		.CLR(din[1])
	);
	endmodule
module clb_LDC_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y121";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDC_1 ff (
		.G(clk),
		.Q(dout),
		.D(din[0]),
		.CLR(din[1])
	);
	endmodule

module clb_LDCE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y122";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDCE ff (
		.G(clk),
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDCE_1 ff (
		.G(clk),
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
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDE ff (
		.G(clk),
		.Q(dout),
		.D(din[0]),
		.GE(din[1])
	);
	endmodule
module clb_LDE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y125";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDE_1 ff (
		.G(clk),
		.Q(dout),
		.D(din[0]),
		.GE(din[1])
	);
	endmodule

module clb_LDP (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y126";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDP ff (
		.G(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule
module clb_LDP_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y127";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDP_1 ff (
		.G(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_LDPE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y128";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDPE ff (
		.G(clk),
		.Q(dout),
		.PRE(din[0]),
		.D(din[1]),
		.GE(din[2])
	);
	endmodule
module clb_LDPE_1 (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y129";
    parameter BEL="AFF";
	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LDPE_1 ff (
		.G(clk),
		.Q(dout),
		.PRE(din[0]),
		.D(din[1]),
		.GE(din[2])
	);
	endmodule

