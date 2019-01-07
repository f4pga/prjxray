`include "setseed.vh"

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 10;
	localparam integer DOUT_N = 10;

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

module roi(input clk, input [9:0] din, output [9:0] dout);
	localparam integer N = 200;

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

	wire [N*10+9:0] nets;

	assign nets[9:0] = din;
	assign dout = nets[N*10+9:N*10];

	genvar i, j;
	generate
		for (i = 0; i < N; i = i+1) begin:is
			for (j = 0; j < 10; j = j+1) begin:js
				localparam integer k = i*10 + j + 10;
				wire lut_out;

				LUT6 #(
					.INIT(hash64({i, j, 8'hff}))
				) lut (
					.I0(nets[hash32({i, j, 8'h00}) % k]),
					.I1(nets[hash32({i, j, 8'h01}) % k]),
					.I2(nets[k-10]),
					.I3(nets[k-9]),
					.I4(nets[k-8]),
					.I5(nets[k-7]),
					.O(lut_out)
				);

				reg lut_out_reg;
				always @(posedge clk)
					lut_out_reg <= lut_out;

				assign nets[k] = ((i+j) % 17) < 10 ? lut_out_reg : lut_out;
			end
		end
	endgenerate
endmodule
