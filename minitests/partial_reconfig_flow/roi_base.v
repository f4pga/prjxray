//See README and tcl for more info

`include "defines.v"

module roi(input clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;
endmodule
