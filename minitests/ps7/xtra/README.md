# PS7 verilog cell definition extractor

Extracts all pins of the PS7 bel from Vivado, groups them into buses, removes those that are not connected (TEST*, DEBUG*) and creates the VPR counterpart for it. It also generates model XML, pb_type XML and techmap which handles unconnected ports correctly.
