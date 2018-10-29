//Need at least one LUT per frame base address we want
`define N_LUT 100
`define N_BRAM 8
`define N_IOB 250

module top(input clk, stb, [DIN_N-1:0] di, output do);
	// 3 IOB's are used for clk, stb, and do.
	// Rest are wired to di.
	parameter integer DIN_N = `N_IOB - 3;
	parameter integer DOUT_N = `N_LUT + `N_BRAM;

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
		.din(din[7:0]),
		.dout(dout)
	);
endmodule

module roi(input clk, input [7:0] din, output [`N_LUT + `N_BRAM-1:0] dout);
	genvar i;
	generate
		for (i = 0; i < `N_LUT; i = i+1) begin:luts
			LUT6 #(
				.INIT(64'h8000_0000_0000_0001 + (i << 16))
			) lut (
				.I0(din[0]),
				.I1(din[1]),
				.I2(din[2]),
				.I3(din[3]),
				.I4(din[4]),
				.I5(din[5]),
				.O(dout[i])
			);
		end
	endgenerate

	genvar j;
	generate
		for (j = 0; j < `N_BRAM; j = j+1) begin:brams
            (* KEEP, DONT_TOUCH *)
            RAMB36E1 #(
                    .INIT_00(256'h8000000000000000000000000000000000000000000000000000000000000000 + (j << 16))
                ) bram (
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
                    .DOADO(dout[j + `N_LUT]),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());
		end
	endgenerate
endmodule
