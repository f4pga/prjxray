module top (input ci, input cyinit, input s0, output o0);
	wire [3:0] o, passthru_co, passthru_o;

	CARRY4 carry4_inst (
		// This will produce the following warning, but will still generate a bitstream.. needs some testing in hardware.
		// WARNING: [DRC REQP-16] virt5_carry4_input_rule1: CYINIT and CI of carry4_inst cannot be used at the same time.
		.CI(passthru_co[3]),
		.CYINIT(cyinit),
		.DI(4'b0000),
		.S({3'b000, s0}),
		.O(o)
	);

	CARRY4 carry4_passthru (
		.CI(1'b1),
		.CYINIT(1'b1),
		.DI({ci, 3'b000}),
		.S(4'b0000),
		.CO(passthru_co)
	);

	assign o0 = o[0];
endmodule
