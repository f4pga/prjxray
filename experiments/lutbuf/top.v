`include "setseed.vh"

`define N 500

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 6;
	localparam integer DOUT_N = `N;

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

module roi(input clk, input [5:0] din, output [`N-1:0] dout);
	function [31:0] xorshift32(input [31:0] v);
		begin
			xorshift32 = v;
			xorshift32 = xorshift32 ^ (xorshift32 << 13);
			xorshift32 = xorshift32 ^ (xorshift32 >> 17);
			xorshift32 = xorshift32 ^ (xorshift32 <<  5);
		end
	endfunction

	function [31:0] hash32(input [31:0] v);
		begin
			hash32 = v ^ `SEED;
			hash32 = xorshift32(hash32);
			hash32 = xorshift32(hash32);
			hash32 = xorshift32(hash32);
			hash32 = xorshift32(hash32);
		end
	endfunction

	function [63:0] hash64(input [31:0] v);
		begin
			hash64[63:32] = hash32(v);
			hash64[31: 0] = hash32(~v);
		end
	endfunction

	genvar i;
	generate
		for (i = 0; i < `N; i = i+1) begin:is
			wire o6;
			//Randomly take out 1/4 iterations
			wire [3:0] hash = hash32(i);
			wire opt_out = |hash;
			assign dout[i] = o6 & opt_out;

			LUT6 #(
				.INIT(hash64(i))
			) lut6 (
				.I0(din[0]),
				.I1(din[1]),
				.I2(din[2]),
				.I3(din[3]),
				.I4(din[4]),
				.I5(din[5]),
				.O(o6)
			);
		end
	endgenerate
endmodule
