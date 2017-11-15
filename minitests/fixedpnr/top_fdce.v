
module top(input clk, ce, sr, d, output q);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	FDCE ff (
		.C(clk),
		.CE(ce),
		.CLR(sr),
		.D(d),
		.Q(q)
	);
endmodule

