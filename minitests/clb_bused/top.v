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
    clb_FF clb_FF       (.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    clb_OUT clb_OUT       (.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
endmodule


module clb_FF (input clk, input [7:0] din, output [7:0] dout);
    wire o6;
    //assign dout[0] = o6;

	(* LOC="SLICE_X18Y100", BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(o6));

	(* LOC="SLICE_X18Y100", BEL="BFF" *)
	FDPE ff (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(o6));
endmodule

module clb_OUT (input clk, input [7:0] din, output [7:0] dout);
    wire o6;
    assign dout[0] = o6;

	(* LOC="SLICE_X18Y101", BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O(o6));

	(* LOC="SLICE_X18Y101", BEL="BFF" *)
	FDPE ff (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(o6));
endmodule

