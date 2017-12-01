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
    clb_LUT6 clb_LUT6       (.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0]));
    clb_LUT6_2 clb_LUT6_2   (.clk(clk), .din(din[  8 +: 8]), .dout(dout[  1 +: 2]));
    clb_LUT7A clb_LUT7A     (.clk(clk), .din(din[  16 +: 8]), .dout(dout[  3]));
    clb_LUT7B clb_LUT7B     (.clk(clk), .din(din[  24 +: 8]), .dout(dout[  4]));
    clb_LUT7AB clb_LUT7AB   (.clk(clk), .din(din[  32 +: 8]), .dout(dout[  5 +: 2]));
    clb_LUT8 clb_LUT8       (.clk(clk), .din(din[  40 +: 8]), .dout(dout[  7]));
    
    /*
    BOUTMUX tests
    -CY: carry chain, skip for now
    -F8: already have above
    -O6: easy
    -O5: easy
    -XOR: carry, skip for now
    -B5Q: easy
    */
    clb_BOUTMUX_CY clb_BOUTMUX_CY       (.clk(clk), .din(din[  64 +: 8]), .dout(dout[  8]));
    clb_BOUTMUX_F8 clb_BOUTMUX_F8       (.clk(clk), .din(din[  72 +: 8]), .dout(dout[  9]));
    clb_BOUTMUX_O6 clb_BOUTMUX_O6       (.clk(clk), .din(din[  80 +: 8]), .dout(dout[  10]));
    clb_BOUTMUX_O5 clb_BOUTMUX_O5       (.clk(clk), .din(din[  88 +: 8]), .dout(dout[  11 +: 2]));
    clb_BOUTMUX_B5Q_IN_A clb_BOUTMUX_B5Q_IN_A     (.clk(clk), .din(din[  96 +: 8]), .dout(dout[  13 +: 2]));
    clb_BOUTMUX_B5Q_IN_B clb_BOUTMUX_B5Q_IN_B     (.clk(clk), .din(din[  104 +: 8]), .dout(dout[  15 +: 2]));
    clb_BOUTMUX_XOR clb_BOUTMUX_XOR     (.clk(clk), .din(din[  112 +: 8]), .dout(dout[ 17 ]));
    clb_CARRY4 clb_CARRY4 (.clk(clk), .din(din[  120 +: 16]), .dout(dout[18 +: 8]));

    //CYINT
    clb_CYINT_0 clb_CYINT_0 (.clk(clk), .din(din[  192 +: 8]), .dout(dout[192 +: 8]));
    clb_CYINT_1 clb_CYINT_1 (.clk(clk), .din(din[  200 +: 8]), .dout(dout[200 +: 8]));
    clb_CYINT_AX clb_CYINT_AX (.clk(clk), .din(din[  208 +: 8]), .dout(dout[208 +: 8]));
    clb_CYINT_CIN clb_CYINT_CIN (.clk(clk), .din(din[  216 +: 8]), .dout(dout[216 +: 8]));

    clb_N5FFMUX  # (.LOC("SLICE_X22Y100"), .N(0))
        clb_N5FFMUX_0 (.clk(clk), .din(din[  224 +: 8]), .dout(dout[224 +: 8]));
    clb_N5FFMUX  # (.LOC("SLICE_X22Y101"), .N(1))
        clb_N5FFMUX_1 (.clk(clk), .din(din[  232 +: 8]), .dout(dout[232 +: 8]));
    clb_N5FFMUX  # (.LOC("SLICE_X22Y102"), .N(2))
        clb_N5FFMUX_2 (.clk(clk), .din(din[  240 +: 8]), .dout(dout[240 +: 8]));
    clb_N5FFMUX  # (.LOC("SLICE_X22Y103"), .N(3))
        clb_N5FFMUX_3 (.clk(clk), .din(din[  248 +: 8]), .dout(dout[248 +: 8]));
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

module clb_LUT6_2 (input clk, input [7:0] din, output [1:0] dout);
    wire o6, o5;
    assign dout[1] = o6;
    assign dout[0] = o5;
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

module clb_LUT7AB (input clk, input [7:0] din, output [1:0] dout);
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    assign dout[1] = lut7bo;
    assign dout[0] = lut7ao;

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






//******************************************************************************
//BOUTMUX tests

module clb_BOUTMUX_CY (input clk, input [7:0] din, output dout);
    //Shady connections, just enough to keep it placed
    wire [3:0] cout;
    assign dout = cout[1];

	(* LOC="SLICE_X18Y100", KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(), .CO(cout), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[0]), .CI());
endmodule

//clb_BOUTMUX_F8: already have above as clb_LUT8
module clb_BOUTMUX_F8 (input clk, input [7:0] din, output dout);
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    (* LOC="SLICE_X18Y101", BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout), .I0(lut7bo), .I1(lut7ao), .S(din[7]));
    (* LOC="SLICE_X18Y101", BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC="SLICE_X18Y101", BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

	(* LOC="SLICE_X18Y101", BEL="D6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC="SLICE_X18Y101", BEL="C6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC="SLICE_X18Y101", BEL="B6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC="SLICE_X18Y101", BEL="A6LUT", KEEP, DONT_TOUCH *)
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

module clb_BOUTMUX_O6 (input clk, input [7:0] din, output dout);
	(* LOC="SLICE_X18Y102", BEL="B6LUT", KEEP, DONT_TOUCH *)
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

module clb_BOUTMUX_O5 (input clk, input [7:0] din, output [1:0] dout);
    wire o5, o6;
    assign dout[1] = o5;
    assign dout[0] = o6;
	(* LOC="SLICE_X18Y103", BEL="B6LUT", KEEP, DONT_TOUCH *)
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

//B5FFMUX positions

module clb_BOUTMUX_B5Q_IN_A (input clk, input [7:0] din, output [1:0] dout);
    wire o5;
    wire o6;
    assign dout[0] = o6;
	(* LOC="SLICE_X18Y104", BEL="B6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC="SLICE_X18Y104", BEL="B5FF" *)
	FDPE ff (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(o5)
	);
endmodule

//FIXME: failed
module clb_BOUTMUX_B5Q_IN_B (input clk, input [7:0] din, output [1:0] dout);
	(* LOC="SLICE_X18Y105", BEL="B5FF" *)
	FDPE ff (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
endmodule

//clb_BOUTMUX_XOR: carry, skip for now
module clb_BOUTMUX_XOR (input clk, input [7:0] din, output dout);
    //Shady connections, just enough to keep it placed
    wire [3:0] o;
    assign dout = o[1];

	(* LOC="SLICE_X18Y106", KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[0]), .CI());
endmodule

module clb_CARRY4 (input clk, input [15:0] din, output [7:0] dout);
    //CARRY4 carry4(.O(dout[3:0]), .CO(dout[7:4]), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[8]), .CI(din[9]));
    //CI must come from an adjacent CARRY4
    //CO however is routable out
    //Note: its folding the FFs in
    //are they in bypass? is that a thing?
    //I bet they are setup as latches
	(* LOC="SLICE_X18Y107", KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(dout[3:0]), .CO(dout[7:4]), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[8]), .CI());
endmodule


//****************************************************************
//CYINT

module clb_CYINT_0 (input clk, input [7:0] din, output [7:0] dout);
    wire [3:0] o;
    assign dout[0] = o[1];

	(* LOC="SLICE_X20Y100", KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(1'b0), .CI());
endmodule

module clb_CYINT_1 (input clk, input [7:0] din, output [7:0] dout);
    wire [3:0] o;
    assign dout[0] = o[1];

	(* LOC="SLICE_X20Y101", KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(1'b1), .CI());
endmodule

module clb_CYINT_AX (input clk, input [7:0] din, output [7:0] dout);
    wire [3:0] o;
    assign dout[0] = o[1];

	(* LOC="SLICE_X20Y102", KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[0]), .CI());
endmodule

module clb_CYINT_CIN (input clk, input [7:0] din, output [7:0] dout);
    wire [3:0] coutl;
    wire [3:0] outr;
    assign dout[0] = outr[1];

    //Hmm it actually goes by Y, not L/R as shown in wire layout
	(* LOC="SLICE_X20Y103", KEEP, DONT_TOUCH *)
    CARRY4 carry4l(.O(), .CO(coutl), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[8]), .CI());

	(* LOC="SLICE_X20Y104", KEEP, DONT_TOUCH *)
    CARRY4 carry4r(.O(outr), .CO(), .DI(din[3:0]), .S(din[7:4]), .CYINIT(din[8]), .CI(coutl[3]));
endmodule


//N5FFMUX

module clb_N5FFMUX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=-1;
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    reg [3:0] ffds;
    wire lutdo5, lutco5, lutbo5, lutao5;
    always @(*) begin
        /*
        ffds[3] = lutdo5;
        ffds[2] = lutco5;
        ffds[1] = lutbo5;
        ffds[0] = lutao5;

        ffds[3] = din[6];
        ffds[2] = din[6];
        ffds[1] = din[6];
        ffds[0] = din[6];
        */

        ffds[3] = lutdo5;
        ffds[2] = lutco5;
        ffds[1] = lutbo5;
        ffds[0] = lutao5;
        ffds[N] = din[6];
    end

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

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
		.O5(lutdo5),
		.O6(lutdo));
	(* LOC=LOC, BEL="D5FF" *)
	FDPE ffd (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[3]));

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
		.O5(lutco5),
		.O6(lutco));
	(* LOC=LOC, BEL="C5FF" *)
	FDPE ffc (
		.C(clk),
		.Q(dout[2]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[2]));

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
		.O5(lutbo5),
		.O6(lutbo));
	(* LOC=LOC, BEL="B5FF" *)
	FDPE ffb (
		.C(clk),
		.Q(dout[3]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[1]));

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
		.O5(lutao5),
		.O6(lutao));
	(* LOC=LOC, BEL="A5FF" *)
	FDPE ffa (
		.C(clk),
		.Q(dout[4]),
		.CE(din[0]),
		.PRE(din[1]),
		//D can only come from O5 or AX
		//AX is used by MUXF7:S
		.D(ffds[0]));
endmodule

