
module top(input clk, ce, sr, d, output q);
    /*
    IS_C_INVERTED=1'b1, IS_D_INVERTED=1'b1, IS_CLR_INVERTED=1'b1,
    ERROR: [Place 30-1008] Instance ff has an inverted D pin which is expected to be used as an I/O flop.
    However, it is used as a regular flop. 

    cliff didn't have constrained, also got annoyed
    he is using slightly later version
    ERROR: [Place 30-1008] Instance roi/ffs[0].genblk1.genblk1.ff
    has an inverted D pin which is unsupported in the UltraScale and UltraScale+ architectures.

    which is fine except...he's using 7 series


    and now...
    IS_C_INVERTED=1'b1, IS_D_INVERTED=1'b0, IS_CLR_INVERTED=1'b1,
    ERROR: [Place 30-488] Failed to commit 1 instances:
    ff with block Id: 4 (FF) at SLICE_X0Y104
    ERROR: [Place 30-99] Placer failed with error: 'failed to commit all instances'

    IS_C_INVERTED=1'b0, IS_D_INVERTED=1'b0, IS_CLR_INVERTED=1'b1,
    failed with same message

    IS_C_INVERTED=1'b1, IS_D_INVERTED=1'b0, IS_CLR_INVERTED=1'b0,
    built!
    diff design_fdce.segd design_fdce_inv.segd
        > tag CLBLL_L.SLICEL_X0.CLKINV
    expected

    IS_C_INVERTED=1'b0, IS_D_INVERTED=1'b1, IS_CLR_INVERTED=1'b0,
    ERROR: [Place 30-1008] Instance ff has an inverted D pin which is expected to be used as an I/O flop.
    However, it is used as a regular flop. 
    ERROR: [Place 30-99] Placer failed with error: 'IO Clock Placer stopped due to earlier errors.
    Implementation Feasibility check failed, Please see the previously displayed individual error or warning messages for more details.'
    */
	(*
        IS_C_INVERTED=1'b1, IS_D_INVERTED=1'b0, IS_CLR_INVERTED=1'b0,
	    LOC="SLICE_X16Y100", BEL="AFF", DONT_TOUCH
    *)
	FDCE ff (
		.C(clk),
		.CE(ce),
		.CLR(sr),
		.D(d),
		.Q(q)
	);
endmodule

