module top (input c, d, output q);
	(* LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH *)
	FDRE ff (
		.C(c),
		.CE(1'b1),
		.R(1'b0),
		.D(d),
		.Q(q)
	);
endmodule
