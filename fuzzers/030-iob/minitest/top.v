/*
IOBUF
    Not a primitive?
    Looks like it has an OBUFT


Output buffer family:
    OBUF
    OBUFDS
    OBUFT
    OBUFTDS
*/

`ifndef ROI
ERROR: must set ROI
`endif

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 256;
	localparam integer DOUT_N = 256;

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

    `ROI
	    roi (
		.clk(clk),
		.din(din),
		.dout(dout)
	);
endmodule

module roi_io_a(input clk, input [255:0] din, output [255:0] dout);
    assign dout[0] = din[0] & din[1];

    IOBUF_INTERMDISABLE #(
        .DRIVE(12),
        .IBUF_LOW_PWR("TRUE"),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW"),
        .USE_IBUFDISABLE("TRUE")
    ) IOBUF_INTERMDISABLE_inst (
        .O(1'b0),
        .IO(1'bz),
        .I(dout[8]),
        .IBUFDISABLE(1'b0),
        .INTERMDISABLE(1'b0),
        .T(1'b1));

endmodule

module roi_io_b(input clk, input [255:0] din, output [255:0] dout);
    assign dout[0] = din[0] & din[1];

    wire onet;

    IOBUF_INTERMDISABLE #(
        .DRIVE(12),
        .IBUF_LOW_PWR("FALSE"),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW"),
        .USE_IBUFDISABLE("FALSE")
    ) IOBUF_INTERMDISABLE_inst (
        .O(onet),
        .IO(1'bz),
        .I(dout[8]),
        .IBUFDISABLE(1'b0),
        .INTERMDISABLE(1'b0),
        .T(1'b1));

    PULLUP PULLUP_inst (
        .O(onet)
    );

    IOBUF_INTERMDISABLE #(
        .DRIVE(12),
        .IBUF_LOW_PWR("FALSE"),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW"),
        .USE_IBUFDISABLE("FALSE")
    ) i2 (
        .O(),
        .IO(1'bz),
        .I(dout[8]),
        .IBUFDISABLE(1'b0),
        .INTERMDISABLE(1'b0),
        .T(1'b1));

endmodule

/*
For some reason this doesn't diff
Was this optimized out?

ERROR: [Place 30-69] Instance roi/dut/OBUFT (OBUFT) is unplaced after IO placer
ERROR: [Place 30-68] Instance roi/dut/OBUFT (OBUFT) is not placed
*/

/*
module roi_prop_a(input clk, input [255:0] din, output [255:0] dout);
    assign dout[0] = din[0] & din[1];

    //(* LOC="D19", KEEP, DONT_TOUCH *)
    (* KEEP, DONT_TOUCH *)
    IOBUF #(
        .DRIVE(8),
        .IBUF_LOW_PWR("TRUE"),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW")
    ) dut (
        .O(dout[1]),
        .I(din[0]),
        .T(din[1]));
endmodule

module roi_prop_b(input clk, input [255:0] din, output [255:0] dout);
    assign dout[0] = din[0] & din[1];

    //(* LOC="D19", KEEP, DONT_TOUCH *)
    (* KEEP, DONT_TOUCH *)
    IOBUF #(
        .DRIVE(12),
        .IBUF_LOW_PWR("TRUE"),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW")
    ) dut (
        .O(dout[1]),
        .I(din[0]),
        .T(din[1]));
endmodule
*/

/*
ERROR: [DRC REQP-1581] obuf_loaded: OBUFT roi/dut pin O drives one or more invalid loads. The loads are: dout_shr[1]_i_1
ERROR: [Place 30-69] Instance roi/dut (OBUFT) is unplaced after IO placer
hmm
Abandoning verilog approach
tcl seems to work well, just use it directly
*/
module roi_prop_a(input clk, input [255:0] din, output [255:0] dout);
    (* LOC="D19", KEEP, DONT_TOUCH *)
    //(* KEEP, DONT_TOUCH *)
    OBUFT #(
        .DRIVE(8),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW")
    ) dut (
        //.O(dout[1]),
        .O(),
        .I(din[0]),
        .T(din[1]));
endmodule

module roi_prop_b(input clk, input [255:0] din, output [255:0] dout);
    (* LOC="D19", KEEP, DONT_TOUCH *)
    //(* KEEP, DONT_TOUCH *)
    (* KEEP, DONT_TOUCH *)
    OBUFT #(
        .DRIVE(12),
        .IOSTANDARD("DEFAULT"),
        .SLEW("SLOW")
    ) dut (
        //.O(dout[1]),
        .O(),
        .I(din[0]),
        .T(din[1]));
endmodule


