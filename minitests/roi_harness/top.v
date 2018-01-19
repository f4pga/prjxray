//See README and tcl for more info

`include "defines.v"

module top(input wire clk,
        inout wire [DIN_N-1:0] din, inout wire [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    /*
    //Added explicit I/O as clocking was doing something weird
    (* KEEP, DONT_TOUCH *)
    wire clk_net;
    (* KEEP, DONT_TOUCH *)
    wire [DIN_N-1:0] din_net;
    (* KEEP, DONT_TOUCH *)
    wire [DOUT_N-1:0] dout_net;
    genvar i;
    generate
        //CLK
        (* KEEP, DONT_TOUCH *)
        BUFG bufg(.I(clk), .O(clk_net));

        //DIN
        for (i = 0; i < DIN_N; i = i+1) begin:ins
            IOBUF bufio(.O(din_net[i]), .IO(din[i]), .I(1'bx), .T(1'b0));
        end

        //DOUT
        for (i = 0; i < DOUT_N; i = i+1) begin:outs
            IOBUF bufio(.O(), .IO(dout[i]), .I(dout_net[i]), .T(1'b1));
        end
    endgenerate

    roi #(.DIN_N(DIN_N), .DOUT_N(DOUT_N)) roi (
        .clk(clk_net),
        .din(din_net), .dout(dout_net));
    */
    roi #(.DIN_N(DIN_N), .DOUT_N(DOUT_N)) roi (
        .clk(clk),
        .din(din), .dout(dout));
endmodule

