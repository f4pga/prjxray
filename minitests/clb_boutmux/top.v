//move some stuff to minitests/ncy0

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

module roi(input clk, input [255:0] din, output [255:0] dout);
    clb_BOUTMUX_CY clb_BOUTMUX_CY       (.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    clb_BOUTMUX_F8 clb_BOUTMUX_F8       (.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    clb_BOUTMUX_O6 clb_BOUTMUX_O6       (.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    clb_BOUTMUX_O5 clb_BOUTMUX_O5       (.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    clb_BOUTMUX_B5Q clb_BOUTMUX_B5Q     (.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    clb_BOUTMUX_XOR clb_BOUTMUX_XOR     (.clk(clk), .din(din[  40 +: 8]), .dout(dout[ 40 +: 8 ]));
endmodule

module myLUT8 (input clk, input [7:0] din, output lut8o, output [3:0] co, output [3:0] cout, output bo5, output bo6);
    parameter LOC="SLICE_X18Y101";

    wire [3:0] lutno6;
    wire [3:0] lutno5;
    wire lut7bo, lut7ao;
    assign bo5 = lutno5[1];
    assign bo6 = lutno6[1];

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

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(co), .CO(cout), .DI(din[3:0]), .S(lutno6), .CYINIT(1'b0), .CI());
endmodule

//******************************************************************************
//BOUTMUX tests

module clb_BOUTMUX_CY (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X18Y100";

    wire [3:0] cout;
    assign dout = cout[1];
    myLUT8 #(.LOC(LOC))
            myLUT8(.clk(clk), .din(din), .lut8o(), .cout(cout));
endmodule

//clb_BOUTMUX_F8: already have above as clb_LUT8
module clb_BOUTMUX_F8 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X18Y101";

    myLUT8 #(.LOC(LOC))
            myLUT8(.clk(clk), .din(din), .lut8o(dout[0]), .cout());
endmodule

/*
FIXME: need to force it to use both X and O6
*/
module clb_BOUTMUX_O6 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X18Y102";

    myLUT8 #(.LOC(LOC))
            myLUT8(.clk(clk), .din(din), .lut8o(), .cout());
endmodule

module clb_BOUTMUX_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X18Y103";

    myLUT8 #(.LOC(LOC))
            myLUT8(.clk(clk), .din(din), .lut8o(), .cout(), .bo5(dout[1]), .bo6(dout[0]));
endmodule

module clb_BOUTMUX_B5Q (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X18Y104";

    myLUT8 #(.LOC(LOC))
            myLUT8(.clk(clk), .din(din), .cout());

	(* LOC=LOC, BEL="B5FF" *)
	FDPE ff (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
endmodule

module clb_BOUTMUX_XOR (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X18Y105";

    //Shady connections, just enough to keep it placed
    wire [3:0] co;
    assign dout = co[1];

    myLUT8 #(.LOC(LOC))
            myLUT8(.clk(clk), .din(din), .lut8o(), .co(co), .cout(), .bo5(), .bo6());
endmodule

