module top(input clk, di, output do);
	roi roi (
		.clk(clk),
		.din(di),
		.dout(do)
	);
endmodule

module roi(input clk, input din, output dout);
	localparam integer N = 500;

	wire [N:0] nets;

	assign nets[0] = din;
	assign dout = nets[N];

	genvar i;
	generate
		for (i = 0; i < N; i = i+1) begin:ffs
			FDRE ff (
				.C(clk),
				.D(nets[i]),
				.Q(nets[i+1]),
				.R(1'b0),
				.CE(1'b1)
			);
		end
	endgenerate
endmodule
