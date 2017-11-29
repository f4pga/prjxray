
module top(input clk, ce, sr, d, output q);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	//Keep inverter off
	LDCE_1 ff (
		.G(clk),
		.GE(ce),
		.CLR(sr),
		.D(d),
		.Q(q)
	);
endmodule

