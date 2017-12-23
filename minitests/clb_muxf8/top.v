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
    my_mux8_full  # (.LOC("SLICE_X22Y100"))
        c0 (.clk(clk), .din(din[  0 +: 8]), .dout(dout[0 +: 8]));
endmodule

//works
module my_mux8 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=-1;
    parameter DEF_A=1;

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout[0]), .I0(1'b0), .I1(1'b1), .S(din[6]));
endmodule

//works
module my_mux78 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=-1;
    parameter DEF_A=1;

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout[0]), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(1'b0), .I1(1'b1), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(1'b0), .I1(1'b1), .S(din[6]));
endmodule

//works
//connects inputs to LUT outputs, which are presumably driven into constant output mode
module my_mux78x (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    wire lut7bo, lut7ao;

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout[0]), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(1'bx), .I1(1'bx), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(1'bx), .I1(1'bx), .S(din[6]));
endmodule

//Switch MUX8 positions
//Fail
//Bel does not match with the valid locations at which this inst can be placed
module my_mux78x_switch (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    wire lut7bo, lut7ao;

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout[0]), .I0(lut7ao), .I1(lut7bo), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(1'bx), .I1(1'bx), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(1'bx), .I1(1'bx), .S(din[6]));
endmodule

//works
//Unlike above, this actually makes the inputs N/C
module my_mux78nc (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    wire lut7bo, lut7ao;

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(dout[0]), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(), .I1(), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(), .I1(), .S(din[6]));
endmodule

//works
//mux7/mux8 are completely disconnected
module my_mux78nc2 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    wire lut7bo, lut7ao;

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(), .I1(), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(), .I1(), .S(din[6]));
endmodule

//fail
//Minimal MUX8 placement with actual LUTs
//Doesn't work (3x shape is trying to block LUT error)
module my_mux8_full (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    assign dout[0] = lut8o;
    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 amux8 (.O(lut8o), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 amux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 amux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

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
		.O5(),
		.O6(lutdo));

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
		.O5(),
		.O6(lutco));

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
		.O5(),
		.O6(lutbo));

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
		.O5(),
		.O6(lutao));
endmodule

//Works!
//Very odd
module my_mux8_full_lut6 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    assign dout[0] = lut8o;
    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 amux8 (.O(lut8o), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 amux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 amux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

	(* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
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

	(* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
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

module my_conflict (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=-1;
    parameter DEF_A=1;
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    reg [3:0] ffds;
    wire lutdo5, lutco5, lutbo5, lutao5;
    //wire lutno5 [3:0] = {lutao5, lutbo5, lutco5, lutdo5};
    wire lutno5 [3:0] = {lutdo5, lutco5, lutbo5, lutao5};
    always @(*) begin
        //Default poliarty A
        ffds[3] = lutdo5;
        ffds[2] = lutco5;
        ffds[1] = lutbo5;
        ffds[0] = lutao5;
        ffds[N] = din[6];
    end

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(), .I1(), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(), .I1(), .S(din[6]));

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

module my_mux8_ff (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=0;
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    reg [3:0] ffds;
    wire lutdo5, lutco5, lutbo5, lutao5;
    wire lutno5 [3:0] = {lutdo5, lutco5, lutbo5, lutao5};
    always @(*) begin
        //Default poliarty A
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

