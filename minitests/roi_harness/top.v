//See README and tcl for more info

`include "defines.v"

module top(input wire clk,
        inout wire [DIN_N-1:0] din, output wire [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    roi #(.DIN_N(DIN_N), .DOUT_N(DOUT_N)) roi (
        .clk(clk),
        .din(din), .dout(dout));
endmodule

