module top(input clk, din, stb, output dout);
	reg [39:0] din_bits;
	wire [76:0] dout_bits;

	reg [39:0] din_shr;
	reg [76:0] dout_shr;

	always @(posedge clk) begin
		if (stb) begin
			din_bits <= din_shr;
			dout_shr <= dout_bits;
		end else begin
			din_shr <= {din_shr, din};
			dout_shr <= {dout_shr, din_shr[39]};
		end
	end

	assign dout = dout_shr[76];

	stuff stuff (
		.clk(clk),
		.din_bits(din_bits),
		.dout_bits(dout_bits)
	);
endmodule

module stuff(input clk, input [39:0] din_bits, output [76:0] dout_bits);
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
		.din(din_bits[39:34]),
		.dout(dout_bits[76:71])
	);
endmodule

module randluts(input [5:0] din, output [5:0] dout);
	localparam integer N = 300;

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
			lutinit[63:32] = xorshift32(xorshift32(xorshift32(xorshift32({a, b}))));
			lutinit[31: 0] = xorshift32(xorshift32(xorshift32(xorshift32({b, a}))));
		end
	endfunction

	wire [(N+1)*6-1:0] nets;

	assign nets[5:0] = din;
	assign dout = nets[(N+1)*6-1:N*6];

	genvar i, j;
	generate
		for (i = 0; i < N; i = i+1) begin:is
			for (j = 0; j < 6; j = j+1) begin:js
				LUT6 #(
					.INIT(lutinit(i, j))
				) lut (
					.I0(nets[6*i+0]),
					.I1(nets[6*i+1]),
					.I2(nets[6*i+2]),
					.I3(nets[6*i+3]),
					.I4(nets[6*i+4]),
					.I5(nets[6*i+5]),
					.O(nets[6*i+6+j])
				);
			end
		end
	endgenerate
endmodule
