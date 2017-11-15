
module top(input clk, ce, sr, d, output q);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	FDSE ff (
		.C(clk),
		.CE(ce),
		.S(sr),
		.D(d),
		.Q(q)
	);
endmodule

