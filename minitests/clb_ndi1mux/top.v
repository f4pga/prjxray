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
RAM64X1S: LOCs but doesn't BEL
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

module roi(input clk, input [255:0] din, output [255:0] dout);
`define ALL1
`ifdef ALL1
    //ok
    my_NDI1MUX_NMC31 #(.LOC("SLICE_X8Y100"))
            my_NDI1MUX_NMC31(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    /*
    //Can't find a valid solution
    my_NDI1MUX_NDI1 #(.LOC("SLICE_X8Y101"))
            my_NDI1MUX_NDI1(.clk(clk), .din(din[  8 +: 32]), .dout(dout[  8 +: 8]));
    */
    my_NDI1MUX_NI #(.LOC("SLICE_X8Y102"))
            my_NDI1MUX_NI(.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
`endif

`define SINGLE1
`ifdef SINGLE1
    //ok
    my_ADI1MUX_BMC31 #(.LOC("SLICE_X10Y100"))
            my_ADI1MUX_BMC31(.clk(clk), .din(din[  64 +: 8]), .dout(dout[  64 +: 8]));
    //ok
    my_ADI1MUX_AI #(.LOC("SLICE_X10Y101"))
            my_ADI1MUX_AI(.clk(clk), .din(din[  72 +: 8]), .dout(dout[  72 +: 8]));
    /*
    //bad
    my_ADI1MUX_BDI1 #(.LOC("SLICE_X10Y102"))
            my_ADI1MUX_BDI1(.clk(clk), .din(din[  80 +: 16]), .dout(dout[  80 +: 16]));
    */
    my_BDI1MUX_DI #(.LOC("SLICE_X10Y103"))
            my_BDI1MUX_DI(.clk(clk), .din(din[  96 +: 16]), .dout(dout[  96 +: 16]));
`endif
endmodule


/****************************************************************************
Tries to set all three muxes at once
****************************************************************************/

module my_NDI1MUX_NMC31 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "SLICE_X6Y100";
    wire [3:0] q31;

    (* LOC=LOC, BEL="D6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutd (
            .Q(dout[0]),
            .Q31(q31[3]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL="C6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[1]),
            .Q31(q31[2]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            //.D(din[7]));
            .D(q31[3]));
    (* LOC=LOC, BEL="B6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[2]),
            .Q31(q31[1]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            //.D(din[7]));
            .D(q31[2]));
    (* LOC=LOC, BEL="A6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[3]),
            .Q31(q31[0]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            //.D(din[7]));
            .D(q31[1]));
endmodule

/*
//Cannot loc instance 'roi/my_NDI1MUX_NDI1/lutc' at site SLICE_X6Y100,
//Bel does not match with the valid locations at which this inst can be placed

module my_NDI1MUX_NDI1 (input clk, input [31:0] din, output [7:0] dout);
    parameter LOC = "SLICE_X6Y100";
    wire [3:0] q31;

    (* LOC=LOC, BEL="D6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutd (
            .Q(dout[0]),
            .Q31(q31[3]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL="C6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[1]),
            .Q31(q31[2]),
            .A(din[12:8]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[15]));
    (* LOC=LOC, BEL="B6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[2]),
            .Q31(q31[1]),
            .A(din[20:16]),
            .CE(din[5]),
            .CLK(din[6]),
            //.D(din[23]));
            .D(q31[2]));
    (* LOC=LOC, BEL="A6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[3]),
            .Q31(q31[0]),
            .A(din[28:24]),
            .CE(din[5]),
            .CLK(din[6]),
            //.D(din[31]));
            .D(q31[2]));
endmodule
*/


module my_NDI1MUX_NI (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "SLICE_X6Y100";

    (* LOC=LOC, BEL="D6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutd (
            .Q(dout[0]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL="C6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[1]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL="B6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[2]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL="A6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[3]),
            .Q31(),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
endmodule

/****************************************************************************
Individual mux tests
****************************************************************************/

module my_ADI1MUX_AI (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    wire mc31c;

    (* LOC=LOC, BEL=BEL *)
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

//ok
module my_ADI1MUX_BMC31 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BELO="B6LUT";
    parameter BELI="A6LUT";

    wire mc31b;

    (* LOC=LOC, BEL=BELO *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[0]),
            .Q31(mc31b),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL=BELI *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[1]),
            .Q31(dout[2]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(mc31b));

endmodule

/*
Bad
See my_NDI1MUX_NDI1 for a more serious effort
*/
module my_ADI1MUX_BDI1 (input clk, input [15:0] din, output [15:0] dout);
    parameter LOC = "";
    parameter BELO="C6LUT";
    parameter BELI="A6LUT";

    wire mc31c;
    //wire da = din[6];

    (* LOC=LOC, BEL=BELO *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[0]),
            .Q31(mc31c),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
    (* LOC=LOC, BEL=BELI *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[1]),
            .Q31(dout[2]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(mc31c));
endmodule

module my_BDI1MUX_DI (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "SLICE_X6Y100";
    wire di = din[7];
    wire wemux = din[5];

    (* LOC=LOC, BEL="D6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutd (
            .Q(dout[0]),
            .Q31(),
            .A(din[4:0]),
            .CE(wemux),
            .CLK(clk),
            .D(di));
    (* LOC=LOC, BEL="C6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[1]),
            .Q31(),
            .A(din[4:0]),
            .CE(wemux),
            .CLK(clk),
            .D(din[7]));
    (* LOC=LOC, BEL="B6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[2]),
            .Q31(),
            .A(din[4:0]),
            .CE(wemux),
            .CLK(clk),
            .D(di));
    (* LOC=LOC, BEL="A6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[3]),
            .Q31(),
            .A(din[4:0]),
            .CE(wemux),
            .CLK(clk),
            .D(din[7]));
endmodule

