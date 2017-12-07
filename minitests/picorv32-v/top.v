//move some stuff to minitests/ncy0

`define SEED 32'h12345678

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 42;
	localparam integer DOUT_N = 79;

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

	roi #(.DIN_N(DIN_N), .DOUT_N(DOUT_N))
	    roi (
		.clk(clk),
		.din(din),
		.dout(dout)
	);
endmodule

module roi(input clk, input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
	parameter integer DIN_N = -1;
	parameter integer DOUT_N = -1;

	picorv32 picorv32 (
		.clk(clk),
		.resetn(din[0]),
		.mem_valid(dout[0]),
		.mem_instr(dout[1]),
		.mem_ready(din[1]),
		.mem_addr(dout[33:2]),
		.mem_wdata(dout[66:34]),
		.mem_wstrb(dout[70:67]),
		.mem_rdata(din[33:2])
	);

	randluts randluts (
		.din(din[41:34]),
		.dout(dout[78:71])
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
