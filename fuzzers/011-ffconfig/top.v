`include "setseed.vh"

module top(input clk, rst, di, output do);
	roi roi (
		.clk(clk),
		.rst(rst),
		.din(di),
		.dout(do)
	);
endmodule

module roi(input clk, input rst, input din, output dout);
	localparam integer N = 500;

	wire [N:0] nets;

	assign nets[0] = din;
	assign dout = nets[N];

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

	genvar i;
	generate
		for (i = 0; i < N; i = i+1) begin:ffs
			localparam integer fftype = hash32(i) % 4;
			case (fftype)
				0: begin
					FDRE ff (
						.C(clk),
						.D(nets[i]),
						.Q(nets[i+1]),
						.R(rst),
						.CE(1'b1)
					);
				end
				1: begin
					FDSE ff (
						.C(clk),
						.D(nets[i]),
						.Q(nets[i+1]),
						.S(rst),
						.CE(1'b1)
					);
				end
				2: begin
					FDCE ff (
						.C(clk),
						.D(nets[i]),
						.Q(nets[i+1]),
						.CLR(rst),
						.CE(1'b1)
					);
				end
				3: begin
					FDPE ff (
						.C(clk),
						.D(nets[i]),
						.Q(nets[i+1]),
						.PRE(rst),
						.CE(1'b1)
					);
				end
			endcase
		end
	endgenerate
endmodule
