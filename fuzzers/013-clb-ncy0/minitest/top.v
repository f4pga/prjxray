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
    clb_NCY0_MX # (.LOC("SLICE_X20Y100"), .BEL("A6LUT"), .N(0))
            am (.clk(clk), .din(din[  0 +: 8]), .dout(dout[0 +: 8]));
    clb_NCY0_O5 # (.LOC("SLICE_X20Y101"), .BEL("A6LUT"), .N(0))
            a5 (.clk(clk), .din(din[  8 +: 8]), .dout(dout[8 +: 8]));

    clb_NCY0_MX # (.LOC("SLICE_X20Y102"), .BEL("B6LUT"), .N(1))
            bm (.clk(clk), .din(din[  16 +: 8]), .dout(dout[16 +: 8]));
    clb_NCY0_O5 # (.LOC("SLICE_X20Y103"), .BEL("B6LUT"), .N(1))
            b5 (.clk(clk), .din(din[  24 +: 8]), .dout(dout[24 +: 8]));

    clb_NCY0_MX # (.LOC("SLICE_X20Y104"), .BEL("C6LUT"), .N(2))
            cm (.clk(clk), .din(din[  32 +: 8]), .dout(dout[32 +: 8]));
    clb_NCY0_O5 # (.LOC("SLICE_X20Y105"), .BEL("C6LUT"), .N(2))
            c5 (.clk(clk), .din(din[  40 +: 8]), .dout(dout[40 +: 8]));

    clb_NCY0_MX # (.LOC("SLICE_X20Y106"), .BEL("D6LUT"), .N(3))
            dm (.clk(clk), .din(din[  48 +: 8]), .dout(dout[48 +: 8]));
    clb_NCY0_O5 # (.LOC("SLICE_X20Y107"), .BEL("D6LUT"), .N(3))
            d5 (.clk(clk), .din(din[  56 +: 8]), .dout(dout[56 +: 8]));
endmodule

module clb_NCY0_MX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X16Y129_FIXME";
    parameter BEL="A6LUT_FIXME";
    parameter N=-1;

    wire [3:0] o;
    assign dout[0] = o[1];
    wire o6, o5;
    reg [3:0] s;

    always @(*) begin
        s = din[7:4];
        s[N] = o6;
    end

	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(s), .CYINIT(1'b0), .CI());
endmodule

module clb_NCY0_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X16Y129_FIXME";
    parameter BEL="A6LUT_FIXME";
    parameter N=-1;

    wire [3:0] o;
    assign dout[0] = o[1];
    wire o6, o5;
    reg [3:0] s;
    reg [3:0] di;

    always @(*) begin
        s = din[7:4];
        s[N] = o6;
        
        di = {din[3:0]};
        di[N] = o5;
    end

	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
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

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(di), .S(s), .CYINIT(1'b0), .CI());
endmodule

