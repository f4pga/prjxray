`include "setseed.vh"

module top(input clk, din, stb, output dout);
	reg [41:0] din_bits;
	wire [78:0] dout_bits;

	reg [41:0] din_shr;
	reg [78:0] dout_shr;

	always @(posedge clk) begin
		if (stb) begin
			din_bits <= din_shr;
			dout_shr <= dout_bits;
		end else begin
			din_shr <= {din_shr, din};
			dout_shr <= {dout_shr, din_shr[41]};
		end
	end

	assign dout = dout_shr[78];

	stuff stuff (
		.clk(clk),
		.din_bits(din_bits),
		.dout_bits(dout_bits)
	);
endmodule

module stuff(input clk, input [41:0] din_bits, output [78:0] dout_bits);
	picorv32 picorv32 (
		.clk(clk),
		.resetn(din_bits[0]),
		.mem_valid(dout_bits[0]),
		.mem_instr(dout_bits[1]),
		.mem_ready(din_bits[1]),
		.mem_addr(dout_bits[33:2]),
		.mem_wdata(dout_bits[66:34]),
		.mem_wstrb(dout_bits[70:67]),
		.mem_rdata(din_bits[33:2])
	);

	randluts randluts (
		.din(din_bits[41:34]),
		.dout(dout_bits[78:71])
	);
endmodule

module randluts(input [7:0] din, output [7:0] dout);
	localparam integer N = 250;

	function [31:0] xorshift32(input [31:0] xorin);
		begin
			xorshift32 = xorin;
			xorshift32 = xorshift32 ^ (xorshift32 << 13);
			xorshift32 = xorshift32 ^ (xorshift32 >> 17);
			xorshift32 = xorshift32 ^ (xorshift32 <<  5);
		end
	endfunction

	function [63:0] lutinit(input [7:0] a, b);
		begin
			lutinit[63:32] = xorshift32(xorshift32(xorshift32(xorshift32({a, b} ^ `SEED))));
			lutinit[31: 0] = xorshift32(xorshift32(xorshift32(xorshift32({b, a} ^ `SEED))));
		end
	endfunction

	wire [(N+1)*8-1:0] nets;

	assign nets[7:0] = din;
	assign dout = nets[(N+1)*8-1:N*8];

	genvar i, j;
	generate
		for (i = 0; i < N; i = i+1) begin:is
			for (j = 0; j < 8; j = j+1) begin:js
				localparam integer k = xorshift32(xorshift32(xorshift32(xorshift32((i << 20) ^ (j << 10) ^ `SEED)))) & 255;
				LUT6 #(
					.INIT(lutinit(i, j))
				) lut (
					.I0(nets[8*i+(k+0)%8]),
					.I1(nets[8*i+(k+1)%8]),
					.I2(nets[8*i+(k+2)%8]),
					.I3(nets[8*i+(k+3)%8]),
					.I4(nets[8*i+(k+4)%8]),
					.I5(nets[8*i+(k+5)%8]),
					.O(nets[8*i+8+j])
				);
			end
		end
	endgenerate
endmodule
