module top(input clk, stb, di, output do);
	localparam integer DIN_N = 3;
	localparam integer DOUT_N = 1;

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

module roi(input clk, input [2:0] din, output [0:0] dout);
	(* LOC="SLICE_X12Y102", BEL="AFF" *)
	FDCE ff (
		.C(clk),
		.Q(dout[0]),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
endmodule

