/*
SLICEM at the following:
SLICE_XxY*
Where Y any value
x
    Always even (ie 100, 102, 104, etc)
    In our ROI
    x = 6, 8, 10, 12, 14

SRL16E: LOC + BEL
SRLC32E: LOC + BEL
RAM64X1S: LOCs but doesn't BEL (or maybe I'm using the wrong BEL?)
*/

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


//Activate W*MUX
module roi(input clk, input [255:0] din, output [255:0] dout);
    my_RAM128X1D #(.LOC("SLICE_X12Y100"))
            c0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    /*
    my_RAM128X1D_2 #(.LOC("SLICE_X12Y101"))
            c1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    */
    my_RAM128X1S #(.LOC("SLICE_X12Y102"))
            c2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    my_RAM256X1S #(.LOC("SLICE_X12Y103"))
            c3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
endmodule



//Try to get a conflict on memory LUT vs LUT6_2
module roi_lkjsadfsdf(input clk, input [255:0] din, output [255:0] dout);
    my_multilut #(.LOC("SLICE_X12Y100"))
            c0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

/*
seg SEG_CLBLM_L_X10Y100
bit 00_24
bit 01_23
bit 01_43
bit 30_17
bit 30_46
bit 31_47
*/
module my_multilut (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM64X1S #(
        ) lutd (
            .O(dout[3]),
            .A0(din[0]),
            .A1(din[0]),
            .A2(din[0]),
            .A3(din[0]),
            .A4(din[0]),
            .A5(din[0]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[0]));

    (* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[2]),
            .Q31(),
            .A({din[0], din[0], din[0], din[0], din[0]}),
            .CE(din[0]),
            .CLK(clk),
            .D(din[0]));

    (* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
    SRL16E #(
        ) lutb (
            .Q(dout[1]),
            .A0(din[0]),
            .A1(din[0]),
            .A2(din[0]),
            .A3(din[0]),
            .CE(din[0]),
            .CLK(clk),
            .D(din[0]));

    (* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
    LUT6_2 #(
        .INIT(64'h8000_1CE0_0000_0001)
    ) luta (
        .I0(din[0]),
        .I1(din[0]),
        .I2(din[0]),
        .I3(din[0]),
        .I4(din[0]),
        .I5(din[0]),
        .O5(),
        .O6(dout[0]));
endmodule

//1LUT 4
module roi_(input clk, input [255:0] din, output [255:0] dout);
    my_SRL16E_4 #(.LOC("SLICE_X12Y100"))
            c7(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    my_SRLC32E_4 #(.LOC("SLICE_X12Y101"))
            c3(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    my_RAM32X1S_4 #(.LOC("SLICE_X12Y102"))
            c19(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    my_RAM64X1S_4 #(.LOC("SLICE_X12Y103"))
            c11(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
endmodule

module my_SRL16E_4 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, BEL="D6LUT" *)
    SRL16E #(
        ) lutd (
            .Q(dout[3]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .CE(din[4]),
            .CLK(din[5]),
            .D(din[6]));

    (* LOC=LOC, BEL="C6LUT" *)
    SRL16E #(
        ) lutc (
            .Q(dout[2]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .CE(din[4]),
            .CLK(din[5]),
            .D(din[6]));

    (* LOC=LOC, BEL="B6LUT" *)
    SRL16E #(
        ) lutb (
            .Q(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .CE(din[4]),
            .CLK(din[5]),
            .D(din[6]));

    (* LOC=LOC, BEL="A6LUT" *)
    SRL16E #(
        ) luta (
            .Q(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .CE(din[4]),
            .CLK(din[5]),
            .D(din[6]));
endmodule

module my_SRLC32E_4 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutd (
            .Q(dout[3]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));

    (* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[2]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));

    (* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[1]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));

    (* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[0]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
endmodule

module my_RAM32X1S_4 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC *)
    RAM32X1S #(
        ) lutd (
            .O(dout[3]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));

    (* LOC=LOC *)
    RAM32X1S #(
        ) lutc (
            .O(dout[2]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));

    (* LOC=LOC *)
    RAM32X1S #(
        ) lutb (
            .O(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));

    (* LOC=LOC *)
    RAM32X1S #(
        ) luta (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));
endmodule

module my_RAM64X1S_4 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC *)
    RAM64X1S #(
        ) lutd (
            .O(dout[3]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));

    (* LOC=LOC *)
    RAM64X1S #(
        ) lutc (
            .O(dout[2]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));

    (* LOC=LOC *)
    RAM64X1S #(
        ) lutb (
            .O(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));

    (* LOC=LOC *)
    RAM64X1S #(
        ) luta (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));
endmodule


//1LUT
module roi_asdf(input clk, input [255:0] din, output [255:0] dout);
    //LOCs
    my_SRLC32E #(.LOC("SLICE_X12Y103"), .BEL("D6LUT"))
            c3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));

    //LOCs
    my_SRL16E #(.LOC("SLICE_X12Y107"), .BEL("D6LUT"))
            c7(.clk(clk), .din(din[  56 +: 8]), .dout(dout[  56 +: 8]));

    //No LOC
    my_RAM64X1S #(.LOC("SLICE_X12Y111"), .BEL("D6LUT"))
            c11(.clk(clk), .din(din[  88 +: 8]), .dout(dout[  88 +: 8]));

    //No LOC
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y115"), .BEL("D6LUT"))
            c15(.clk(clk), .din(din[  120 +: 8]), .dout(dout[  120 +: 8]));

    //No LOC
    my_RAM32X1S #(.LOC("SLICE_X12Y119"), .BEL("D6LUT"))
            c19(.clk(clk), .din(din[  152 +: 8]), .dout(dout[  152 +: 8]));

    //No LOC
    my_RAM32X1S_1 #(.LOC("SLICE_X12Y123"), .BEL("D6LUT"))
            c23(.clk(clk), .din(din[  184 +: 8]), .dout(dout[  184 +: 8]));
endmodule


//1LUT
module roi_asdsdaf(input clk, input [255:0] din, output [255:0] dout);
    //LOCs
    my_SRLC32E #(.LOC("SLICE_X12Y100"), .BEL("A6LUT"))
            c0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    my_SRLC32E #(.LOC("SLICE_X12Y101"), .BEL("B6LUT"))
            c1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    my_SRLC32E #(.LOC("SLICE_X12Y102"), .BEL("C6LUT"))
            c2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    my_SRLC32E #(.LOC("SLICE_X12Y103"), .BEL("D6LUT"))
            c3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));

    //LOCs
    my_SRL16E #(.LOC("SLICE_X12Y104"), .BEL("A6LUT"))
            c4(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    my_SRL16E #(.LOC("SLICE_X12Y105"), .BEL("B6LUT"))
            c5(.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
    my_SRL16E #(.LOC("SLICE_X12Y106"), .BEL("C6LUT"))
            c6(.clk(clk), .din(din[  48 +: 8]), .dout(dout[  48 +: 8]));
    my_SRL16E #(.LOC("SLICE_X12Y107"), .BEL("D6LUT"))
            c7(.clk(clk), .din(din[  56 +: 8]), .dout(dout[  56 +: 8]));

    //No LOC
    my_RAM64X1S #(.LOC("SLICE_X12Y108"), .BEL("A6LUT"))
            c8(.clk(clk), .din(din[  64 +: 8]), .dout(dout[  64 +: 8]));
    my_RAM64X1S #(.LOC("SLICE_X12Y109"), .BEL("B6LUT"))
            c9(.clk(clk), .din(din[  72 +: 8]), .dout(dout[  72 +: 8]));
    my_RAM64X1S #(.LOC("SLICE_X12Y110"), .BEL("C6LUT"))
            c10(.clk(clk), .din(din[  80 +: 8]), .dout(dout[  80 +: 8]));
    my_RAM64X1S #(.LOC("SLICE_X12Y111"), .BEL("D6LUT"))
            c11(.clk(clk), .din(din[  88 +: 8]), .dout(dout[  88 +: 8]));

    //No LOC
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y112"), .BEL("A6LUT"))
            c12(.clk(clk), .din(din[  96 +: 8]), .dout(dout[  96 +: 8]));
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y113"), .BEL("B6LUT"))
            c13(.clk(clk), .din(din[  104 +: 8]), .dout(dout[  104 +: 8]));
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y114"), .BEL("C6LUT"))
            c14(.clk(clk), .din(din[  112 +: 8]), .dout(dout[  112 +: 8]));
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y115"), .BEL("D6LUT"))
            c15(.clk(clk), .din(din[  120 +: 8]), .dout(dout[  120 +: 8]));

    //No LOC
    my_RAM32X1S #(.LOC("SLICE_X12Y116"), .BEL("A6LUT"))
            c16(.clk(clk), .din(din[  128 +: 8]), .dout(dout[  128 +: 8]));
    my_RAM32X1S #(.LOC("SLICE_X12Y117"), .BEL("B6LUT"))
            c17(.clk(clk), .din(din[  136 +: 8]), .dout(dout[  136 +: 8]));
    my_RAM32X1S #(.LOC("SLICE_X12Y118"), .BEL("C6LUT"))
            c18(.clk(clk), .din(din[  144 +: 8]), .dout(dout[  144 +: 8]));
    my_RAM32X1S #(.LOC("SLICE_X12Y119"), .BEL("D6LUT"))
            c19(.clk(clk), .din(din[  152 +: 8]), .dout(dout[  152 +: 8]));

    //No LOC
    my_RAM32X1S_1 #(.LOC("SLICE_X12Y120"), .BEL("A6LUT"))
            c20(.clk(clk), .din(din[  160 +: 8]), .dout(dout[  160 +: 8]));
    my_RAM32X1S_1 #(.LOC("SLICE_X12Y121"), .BEL("B6LUT"))
            c21(.clk(clk), .din(din[  168 +: 8]), .dout(dout[  168 +: 8]));
    my_RAM32X1S_1 #(.LOC("SLICE_X12Y122"), .BEL("C6LUT"))
            c22(.clk(clk), .din(din[  176 +: 8]), .dout(dout[  176 +: 8]));
    my_RAM32X1S_1 #(.LOC("SLICE_X12Y123"), .BEL("D6LUT"))
            c23(.clk(clk), .din(din[  184 +: 8]), .dout(dout[  184 +: 8]));
endmodule

//One of each
module roi_asdfsadf(input clk, input [255:0] din, output [255:0] dout);
    //4LUT
    my_RAM64X1D2 #(.LOC("SLICE_X12Y100"))
            c0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    //1LUT
    my_SRLC32E #(.LOC("SLICE_X12Y101"))
            c1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    //1LUT
    my_SRL16E #(.LOC("SLICE_X12Y102"))
            c2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    //4LUT
    my_RAM64M #(.LOC("SLICE_X12Y103"))
            c3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    //1LUT
    my_RAM64X1S #(.LOC("SLICE_X12Y104"))
            c4(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    //1LUT
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y105"))
            c5(.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
    //2LUT
    my_RAM64X2S #(.LOC("SLICE_X12Y106"))
            c6(.clk(clk), .din(din[  48 +: 8]), .dout(dout[  48 +: 8]));
    //2LUT
    my_RAM64X1D #(.LOC("SLICE_X12Y107"))
            c7(.clk(clk), .din(din[  56 +: 8]), .dout(dout[  56 +: 8]));
    //4LUT
    my_RAM128X1D #(.LOC("SLICE_X12Y108"))
            c8(.clk(clk), .din(din[  64 +: 8]), .dout(dout[  64 +: 8]));
    //4LUT
    my_RAM32M #(.LOC("SLICE_X12Y109"))
            c9(.clk(clk), .din(din[  72 +: 8]), .dout(dout[  72 +: 8]));
    //2LUT
    my_RAM32X1D #(.LOC("SLICE_X12Y110"))
            c10(.clk(clk), .din(din[  80 +: 8]), .dout(dout[  80 +: 8]));
    //1LUT
    my_RAM32X1S #(.LOC("SLICE_X12Y111"))
            c11(.clk(clk), .din(din[  88 +: 8]), .dout(dout[  88 +: 8]));
    //1LUT
    my_RAM32X1S_1 #(.LOC("SLICE_X12Y112"))
            c12(.clk(clk), .din(din[  96 +: 8]), .dout(dout[  96 +: 8]));
    //2LUT
    my_RAM32X2S #(.LOC("SLICE_X12Y113"))
            c13(.clk(clk), .din(din[  104 +: 8]), .dout(dout[  104 +: 8]));
endmodule

module roi2(input clk, input [255:0] din, output [255:0] dout);
    /*
    //Test: SRLC32E at each BEL location
    //Takes one LUT
    //BEL works
    my_SRLC32E #(.LOC("SLICE_X12Y100"), .BEL("A6LUT"))
            c0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    my_SRLC32E #(.LOC("SLICE_X12Y101"), .BEL("B6LUT"))
            c1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    my_SRLC32E #(.LOC("SLICE_X12Y102"), .BEL("C6LUT"))
            c2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    my_SRLC32E #(.LOC("SLICE_X12Y103"), .BEL("D6LUT"))
            c3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    */

    //BEL works
    /*
    01_23: common bit
    Seems to be set whenever a SLICEM contains a LUT as RAM element

    D
        01_59
        30_47
    C
        00_28
        30_46
    B
        00_24
        30_17
    A
        00_04
        30_16

    seg SEG_CLBLM_L_X10Y103
    bit 01_23
    bit 01_59
    bit 30_47

    seg SEG_CLBLM_L_X10Y102
    bit 00_28
    bit 01_23
    bit 30_46

    seg SEG_CLBLM_L_X10Y101
    bit 00_24
    bit 01_23
    bit 30_17

    seg SEG_CLBLM_L_X10Y100
    bit 00_04
    bit 01_23
    bit 30_16
    */
    /*
    my_SRL16E #(.LOC("SLICE_X12Y100"), .BEL("A6LUT"))
            c0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    my_SRL16E #(.LOC("SLICE_X12Y101"), .BEL("B6LUT"))
            c1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    my_SRL16E #(.LOC("SLICE_X12Y102"), .BEL("C6LUT"))
            c2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    my_SRL16E #(.LOC("SLICE_X12Y103"), .BEL("D6LUT"))
            c3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    */

    /*
    RAM64M 64-Deep by 4-bit Wide Multi Port Random Access Memory (Select RAM)
    RAM64X1D 64-Deep by 1-Wide Dual Port Static Synchronous RAM
    RAM64X1S 64-Deep by 1-Wide Static Synchronous RAM
    RAM64X1S_1 64-Deep by 1-Wide Static Synchronous RAM with Negative-Edge Clock
    */

    /*
    seg SEG_CLBLM_L_X10Y127
    bit 01_23
    bit 31_16
    bit 31_17
    bit 31_46
    bit 31_47

    seg SEG_CLBLM_L_X10Y100
    bit 01_23
    bit 31_16
    bit 31_17
    bit 31_46
    bit 31_47
    */
    /*
    my_RAM64X1D2 #(.LOC("SLICE_X6Y100"))
            dut0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    my_RAM64X1D2 #(.LOC("SLICE_X6Y127"))
            dut1(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    my_RAM64X1D2 #(.LOC("SLICE_X12Y100"))
            dut2(.clk(clk), .din(din[  64 +: 8]), .dout(dout[  64 +: 8]));
    my_RAM64X1D2 #(.LOC("SLICE_X12Y127"))
            dut3(.clk(clk), .din(din[  128 +: 8]), .dout(dout[  128 +: 8]));
    */



    /*
    seg SEG_CLBLM_L_X10Y105
    bit 00_40
    bit 01_23
    bit 31_16
    bit 31_17
    bit 31_46
    bit 31_47

    seg SEG_CLBLM_L_X10Y104
    bit 01_23
    bit 31_46
    bit 31_47

    seg SEG_CLBLM_L_X10Y103
    bit 01_23
    bit 01_43
    bit 31_46
    bit 31_47

    seg SEG_CLBLM_L_X10Y102
    bit 01_23
    bit 31_47

    seg SEG_CLBLM_L_X10Y101
    bit 01_23
    bit 31_47

    seg SEG_CLBLM_L_X10Y100
    bit 00_00
    bit 00_20
    bit 01_23
    bit 01_43
    bit 31_16
    bit 31_17
    bit 31_46
    bit 31_47
    */
    /*
    my_RAM64M #(.LOC("SLICE_X12Y100"))
            my_RAM64M(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    my_RAM64X1S #(.LOC("SLICE_X12Y101"))
            my_RAM64X1S(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    my_RAM64X1S_1 #(.LOC("SLICE_X12Y102"))
            my_RAM64X1S_1(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    my_RAM64X2S #(.LOC("SLICE_X12Y103"))
            my_RAM64X2S(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    my_RAM64X1D #(.LOC("SLICE_X12Y104"))
            my_RAM64X1D(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    my_RAM128X1D #(.LOC("SLICE_X12Y105"))
            my_RAM128X1D(.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
    */
endmodule

module my_RAM64X1D2 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM64X1D #(
            .INIT(64'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) ramb (
            .DPO(dout[1]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]),
            .A0(din[3]),
            .A1(din[4]),
            .A2(din[5]),
            .A3(din[6]),
            .A4(din[7]),
            .A5(din[0]),
            .DPRA0(din[1]),
            .DPRA1(din[2]),
            .DPRA2(din[3]),
            .DPRA3(din[4]),
            .DPRA4(din[5]),
            .DPRA5(din[6]));

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM64X1D #(
            .INIT(64'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) rama (
            .DPO(dout[0]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]),
            .A0(din[3]),
            .A1(din[4]),
            .A2(din[5]),
            .A3(din[6]),
            .A4(din[7]),
            .A5(din[0]),
            .DPRA0(din[1]),
            .DPRA1(din[2]),
            .DPRA2(din[3]),
            .DPRA3(din[4]),
            .DPRA4(din[5]),
            .DPRA5(din[6]));
endmodule

//BEL: yes
module my_SRLC32E (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    wire mc31c;

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lut (
            .Q(dout[0]),
            .Q31(mc31c),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
endmodule


//BEL: yes
module my_SRL16E (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    SRL16E #(
        ) SRL16E (
            .Q(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .CE(din[4]),
            .CLK(din[5]),
            .D(din[6]));
endmodule

module my_RAM64M (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    RAM64M #(
        ) RAM64M (
            .DOA(dout[0]),
            .DOB(dout[1]),
            .DOC(dout[2]),
            .DOD(dout[3]),
            .ADDRA(din[0]),
            .ADDRB(din[1]),
            .ADDRC(din[2]),
            .ADDRD(din[3]),
            .DIA(din[4]),
            .DIB(din[5]),
            .DIC(din[6]),
            .DID(din[7]),
            .WCLK(clk),
            .WE(din[1]));
endmodule

//Can't get BEL to work. Maybe can't since multiple?
module my_RAM64X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    RAM64X1S #(
        ) RAM64X1S (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));
endmodule

module my_RAM64X1S_1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    RAM64X1S_1 #(
        ) RAM64X1S_1 (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));
endmodule

module my_RAM64X2S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM64X2S #(
        ) RAM64X2S (
            .O0(dout[0]),
            .O1(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D0(din[6]),
            .D1(din[7]),
            .WCLK(clk),
            .WE(din[1]));
endmodule

module my_RAM64X1D (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM64X1D #(
            .INIT(64'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) RAM64X1D (
            .DPO(dout[0]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]),
            .A0(din[3]),
            .A1(din[4]),
            .A2(din[5]),
            .A3(din[6]),
            .A4(din[7]),
            .A5(din[0]),
            .DPRA0(din[1]),
            .DPRA1(din[2]),
            .DPRA2(din[3]),
            .DPRA3(din[4]),
            .DPRA4(din[5]),
            .DPRA5(din[6]));
endmodule

module my_RAM128X1D (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1D #(
            .INIT(128'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) RAM128X1D (
            .DPO(dout[0]),
            .SPO(dout[1]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]));
endmodule

/*
hmm?

CRITICAL WARNING: [Constraints 18-5] Cannot loc instance 'roi/c1/lutb/DP.HIGH' at site SLICE_X12Y101,
Instance roi/c1/lutb/SP.HIGH can not be placed in C6LUT of site SLICE_X12Y101
because the bel is occupied by roi/c1/luta/SP.HIGH(port:). 
This could be caused by bel constraint conflict
*/
module my_RAM128X1D_2 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1D #(
            .INIT(128'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) lutb (
            .DPO(dout[3]),
            .SPO(dout[2]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]));

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1D #(
            .INIT(128'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) luta (
            .DPO(dout[0]),
            .SPO(dout[1]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]));
endmodule

module my_RAM128X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1S #(
        ) RAM128X1S (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .A6(din[6]),
            .D(din[7]),
            .WCLK(din[0]),
            .WE(din[1]));
endmodule

module my_RAM256X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM256X1S #(
        ) RAM256X1S (
            .O(dout[0]),
            .A({din[0], din[7:0]}),
            .D(din[0]),
            .WCLK(din[1]),
            .WE(din[2]));
endmodule

module my_RAM32M (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM32M #(
        ) RAM32M (
            .DOA(dout[1:0]),
            .DOB(dout[3:2]),
            .DOC(dout[5:4]),
            .DOD(dout[7:6]),
            .ADDRA(din[4:0]),
            .ADDRB(din[4:0]),
            .ADDRC(din[4:0]),
            .ADDRD(din[4:0]),
            .DIA(din[5:4]),
            .DIB(din[6:5]),
            .DIC(din[7:6]),
            .DID(din[1:0]),
            .WCLK(din[1]),
            .WE(din[2]));
endmodule

module my_RAM32X1D (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM32X1D #(
        ) RAM32X1D (
            .DPO(dout[0]),
            .SPO(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .DPRA0(din[6]),
            .DPRA1(din[7]),
            .DPRA2(din[0]),
            .DPRA3(din[1]),
            .DPRA4(din[2]),
            .WCLK(din[3]),
            .WE(din[4]));
endmodule

module my_RAM32X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    RAM32X1S #(
        ) RAM32X1S (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));
endmodule

module my_RAM32X1S_1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    RAM32X1S_1 #(
        ) RAM32X1S_1 (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));
endmodule

module my_RAM32X2S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM32X2S #(
        ) RAM32X2S (
            .O0(dout[0]),
            .O1(dout[1]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D0(din[5]),
            .D1(din[6]),
            .WCLK(din[7]),
            .WE(din[0]));
endmodule

