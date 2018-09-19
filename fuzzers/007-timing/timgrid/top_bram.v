`define N 100

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 8;
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

module roi(input clk, input [7:0] din, output [`N-1:0] dout);
	genvar i;
	generate
		for (i = 0; i < `N; i = i+1) begin:is
            (* KEEP, DONT_TOUCH *)
            RAMB36E1 #(.INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000)) ram (
                    .CLKARDCLK(din[0]),
                    .CLKBWRCLK(din[1]),
                    .ENARDEN(din[2]),
                    .ENBWREN(din[3]),
                    .REGCEAREGCE(din[4]),
                    .REGCEB(din[5]),
                    .RSTRAMARSTRAM(din[6]),
                    .RSTRAMB(din[7]),
                    .RSTREGARSTREG(din[0]),
                    .RSTREGB(din[1]),
                    .ADDRARDADDR(din[2]),
                    .ADDRBWRADDR(din[3]),
                    .DIADI(din[4]),
                    .DIBDI(din[5]),
                    .DIPADIP(din[6]),
                    .DIPBDIP(din[7]),
                    .WEA(din[0]),
                    .WEBWE(din[1]),
                    .DOADO(dout[0]),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());
		end
	endgenerate
endmodule

