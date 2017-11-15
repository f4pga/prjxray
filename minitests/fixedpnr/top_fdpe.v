
module top(input clk, ce, sr, d, output q);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	FDPE ff (
		.C(clk),
		.CE(ce),
		.PRE(sr),
		.D(d),
		.Q(q)
	);
endmodule

