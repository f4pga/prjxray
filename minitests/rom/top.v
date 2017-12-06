/*
ROM128X1: 128-Deep by 1-Wide ROM
ROM256X1: 256-Deep by 1-Wide ROM
ROM32X1: 32-Deep by 1-Wide ROM
ROM64X1: 64-Deep by 1-Wide ROM
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
    rom_ROM128X1 #(.LOC("XXX"))
            rom_ROM128X1(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    rom_ROM256X1 #(.LOC("XXX"))
            rom_ROM256X1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    rom_ROM32X1 #(.LOC("XXX"))
            rom_ROM32X1(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    rom_ROM64X1 #(.LOC("XXX"))
            rom_ROM64X1(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
endmodule

//******************************************************************************
//BOUTMUX tests

/*
Cell as SLICEM D6LUT + C6LUT + F7BMUX
*/
module rom_ROM128X1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

    //ROM128X1 #(.LOC(LOC), .N(N))
    ROM128X1 #(.INIT(128'b0))
            rom(
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .A6(din[6]));
endmodule

module rom_ROM256X1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

    ROM256X1 #(.INIT(256'b0))
            rom(
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .A6(din[6]),
            .A7(din[7]));
endmodule

module rom_ROM32X1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

    ROM32X1 #(.INIT(32'b0))
            rom(
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]));
endmodule

module rom_ROM64X1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";

    ROM64X1 #(.INIT(64'b0))
            rom(
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]));
endmodule

