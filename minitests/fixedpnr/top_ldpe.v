
module top(input clk, ce, sr, d, output q);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	LDPE ff (
		.G(clk),
		.GE(ce),
		.PRE(sr),
		.D(d),
		.Q(q)
	);
endmodule

