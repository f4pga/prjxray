`include "defines.v"

module roi(input clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;
endmodule

module top(input wire clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    roi #(.DIN_N(DIN_N), .DOUT_N(DOUT_N)) roi (
        .clk(clk),
        .din(din), .dout(dout));
endmodule

