module top(input clk, stb, di, output do);
	localparam integer DIN_N = 64;
	localparam integer DOUT_N = 8;

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

module roi(input clk, input [63:0] din, output [7:0] dout);
    clb_LUT6 clb_LUT6       (.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0]));
    clb_LUT6_2 clb_LUT6_2   (.clk(clk), .din(din[  8 +: 8]), .dout(dout[  1]));
    clb_LUT7A clb_LUT7A     (.clk(clk), .din(din[  16 +: 8]), .dout(dout[  2]));
    clb_LUT7B clb_LUT7B     (.clk(clk), .din(din[  24 +: 8]), .dout(dout[  3]));
    clb_LUT7AB clb_LUT7AB   (.clk(clk), .din(din[  32 +: 8]), .dout(dout[  4]));
    clb_LUT8 clb_LUT8       (.clk(clk), .din(din[  40 +: 8]), .dout(dout[  5]));
endmodule

module clb_LUT6 (input clk, input [7:0] din, output dout);
	(* LOC="SLICE_X16Y100", BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(dout));
endmodule

module clb_LUT6_2 (input clk, input [7:0] din, output dout);
    wire o5;
    wire o6;
    assign dout = o5 & o6;
	(* LOC="SLICE_X16Y101", BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(o5),
		.O6(o6));
endmodule

module clb_LUT7A (input clk, input [7:0] din, output dout);
    wire lutbo, lutao;

    //F7AMUX
    (* LOC="SLICE_X16Y102", BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(dout), .I0(lutbo), .I1(lutao), .S(din[6]));

	(* LOC="SLICE_X16Y102", BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lut0 (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutbo));

	(* LOC="SLICE_X16Y102", BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lut1 (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutao));
endmodule

module clb_LUT7B (input clk, input [7:0] din, output dout);
    wire lutdo, lutco;

    (* LOC="SLICE_X16Y103", BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(dout), .I0(lutdo), .I1(lutco), .S(din[6]));

	(* LOC="SLICE_X16Y103", BEL="D6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lutd (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutdo));

	(* LOC="SLICE_X16Y103", BEL="C6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutc (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutco));
endmodule

module clb_LUT7AB (input clk, input [7:0] din, output dout);
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    assign dout = lut7bo & lut7ao;

    (* LOC="SLICE_X16Y104", BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));

    (* LOC="SLICE_X16Y104", BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[7]));

	(* LOC="SLICE_X16Y104", BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lut0 (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutbo));

	(* LOC="SLICE_X16Y104", BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lut1 (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutao));

	(* LOC="SLICE_X16Y104", BEL="D6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lutd (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutdo));

	(* LOC="SLICE_X16Y104", BEL="C6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutc (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutco));
endmodule

module clb_LUT8 (input clk, input [7:0] din, output dout);
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    (* LOC="SLICE_X16Y105", BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout), .I0(lut7bo), .I1(lut7ao), .S(din[7]));
    (* LOC="SLICE_X16Y105", BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC="SLICE_X16Y105", BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

	(* LOC="SLICE_X16Y105", BEL="D6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lutd (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutdo));

	(* LOC="SLICE_X16Y105", BEL="C6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutc (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutco));

	(* LOC="SLICE_X16Y105", BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_CAFE_0000_0001)
	) lutb (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutbo));

	(* LOC="SLICE_X16Y105", BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_1CE0_0000_0001)
	) luta (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(lutao));
endmodule

