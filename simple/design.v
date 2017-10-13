module top(input clk, din, stb, output dout);
	reg [33:0] din_bits;
	wire [70:0] dout_bits;

	reg [33:0] din_shr;
	reg [70:0] dout_shr;

	always @(posedge clk) begin
		if (stb) begin
			din_bits <= din_shr;
			dout_shr <= dout_bits;
		end else begin
			din_shr <= {din_shr, din};
			dout_shr <= {dout_shr, din_shr[33]};
		end
	end

	assign dout = dout_shr[70];

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
endmodule
