
module top(input clk, stb, di, output do);
	localparam integer DIN_N = 256;
	localparam integer DOUT_N = 256;

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

(* KEEP_HIERARCHY *)
module roi(input clk, input [255:0] din, output [255:0] dout);
	clb_a clb_a (.clk(clk), .din(din[  0 +: 16]), .dout(dout[  0 +: 16]));
	clb_b clb_b (.clk(clk), .din(din[ 16 +: 16]), .dout(dout[ 16 +: 16]));
	clb_c clb_c (.clk(clk), .din(din[ 32 +: 16]), .dout(dout[ 32 +: 16]));
	clb_d clb_d (.clk(clk), .din(din[ 48 +: 16]), .dout(dout[ 48 +: 16]));
	clb_e clb_e (.clk(clk), .din(din[ 64 +: 16]), .dout(dout[ 64 +: 16]));
	clb_f clb_f (.clk(clk), .din(din[ 80 +: 16]), .dout(dout[ 80 +: 16]));
	clb_g clb_g (.clk(clk), .din(din[ 96 +: 16]), .dout(dout[ 96 +: 16]));
	clb_h clb_h (.clk(clk), .din(din[112 +: 16]), .dout(dout[112 +: 16]));
	clb_i clb_i (.clk(clk), .din(din[128 +: 16]), .dout(dout[128 +: 16]));
	clb_j clb_j (.clk(clk), .din(din[144 +: 16]), .dout(dout[144 +: 16]));
	clb_k clb_k (.clk(clk), .din(din[160 +: 16]), .dout(dout[160 +: 16]));
	clb_l clb_l (.clk(clk), .din(din[176 +: 16]), .dout(dout[176 +: 16]));
	clb_m clb_m (.clk(clk), .din(din[192 +: 16]), .dout(dout[192 +: 16]));
	clb_n clb_n (.clk(clk), .din(din[208 +: 16]), .dout(dout[208 +: 16]));
	clb_o clb_o (.clk(clk), .din(din[224 +: 16]), .dout(dout[224 +: 16]));
	clb_p clb_p (.clk(clk), .din(din[240 +: 16]), .dout(dout[240 +: 16]));
endmodule

// ---------------------------------------------------------------------

module clb_a (input clk, input [15:0] din, output [15:0] dout);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	FDRE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	assign dout[15:1] = 0;
endmodule

module clb_b (input clk, input [15:0] din, output [15:0] dout);
	(* LOC="SLICE_X16Y101", BEL="AFF", DONT_TOUCH *)
	FDSE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	assign dout[15:1] = 0;
endmodule

module clb_c (input clk, input [15:0] din, output [15:0] dout);
	(* LOC="SLICE_X16Y102", BEL="AFF", DONT_TOUCH *)
	FDCE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
	assign dout[15:1] = 0;
endmodule

module clb_d (input clk, input [15:0] din, output [15:0] dout);
	(* LOC="SLICE_X16Y103", BEL="AFF", DONT_TOUCH *)
	FDPE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	assign dout[15:1] = 0;
endmodule

// ---------------------------------------------------------------------

module clb_e (input clk, input [15:0] din, output [15:0] dout);
	wire tmp;

	(* LOC="SLICE_X16Y104", BEL="D6LUT", LOCK_PINS="I0:A1", DONT_TOUCH *)
	LUT1 #(
		.INIT(2'b01)
	) lut (
		.I0(din[2]),
		.O(tmp)
	);

	(* LOC="SLICE_X16Y104", BEL="BFF", DONT_TOUCH *)
	FDRE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.R(din[1]),
		.D(tmp)
	);

	assign dout[15:1] = 0;
endmodule

module clb_f (input clk, input [15:0] din, output [15:0] dout);
	wire tmp;

	(* LOC="SLICE_X16Y105", BEL="D5LUT", LOCK_PINS="I0:A1", DONT_TOUCH *)
	LUT1 #(
		.INIT(2'b01)
	) lut (
		.I0(din[2]),
		.O(tmp)
	);

	(* LOC="SLICE_X16Y105", BEL="BFF", DONT_TOUCH *)
	FDRE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.R(din[1]),
		.D(tmp)
	);

	assign dout[15:1] = 0;
endmodule

module clb_g (input clk, input [15:0] din, output [15:0] dout);
	wire a, b, c;

	(* LOC="SLICE_X16Y106", BEL="D6LUT", LOCK_PINS="I0:A1", DONT_TOUCH *)
	LUT1 #(
		.INIT(2'b01)
	) lut (
		.I0(din[2]),
		.O(a)
	);

	(* LOC="SLICE_X16Y106", BEL="F7BMUX", DONT_TOUCH *)
	MUXF7 mux1 (
		.I0(a),
		.I1(din[3]),
		.S(din[4]),
		.O(b)
	);

	(* LOC="SLICE_X16Y106", BEL="F8MUX", DONT_TOUCH *)
	MUXF8 mux2 (
		.I0(b),
		.I1(din[5]),
		.S(din[6]),
		.O(c)
	);

	(* LOC="SLICE_X16Y106", BEL="BFF", DONT_TOUCH *)
	FDRE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.R(din[1]),
		.D(c)
	);

	assign dout[15:1] = 0;
endmodule

module clb_h (input clk, input [15:0] din, output [15:0] dout);
	wire a, b, c;

	(* LOC="SLICE_X16Y107", BEL="D5LUT", LOCK_PINS="I0:A1", DONT_TOUCH *)
	LUT1 #(
		.INIT(2'b01)
	) lut (
		.I0(din[2]),
		.O(a)
	);

	(* LOC="SLICE_X16Y107", BEL="F7BMUX", DONT_TOUCH *)
	MUXF7 mux1 (
		.I0(a),
		.I1(din[3]),
		.S(din[4]),
		.O(b)
	);

	(* LOC="SLICE_X16Y107", BEL="F8MUX", DONT_TOUCH *)
	MUXF8 mux2 (
		.I0(b),
		.I1(din[5]),
		.S(din[6]),
		.O(c)
	);

	(* LOC="SLICE_X16Y107", BEL="BFF", DONT_TOUCH *)
	FDRE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.R(din[1]),
		.D(c)
	);

	assign dout[15:1] = 0;
endmodule

// ---------------------------------------------------------------------

module clb_i (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_j (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_k (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_l (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_m (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_n (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_o (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

module clb_p (input clk, input [15:0] din, output [15:0] dout);
	assign dout = 0;
endmodule

