//See README and tcl for more info

`ifndef DIN_N
`define DIN_N 4
`endif

`ifndef DOUT_N
`define DOUT_N 4
`endif

module top(input wire clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    roi #(.DIN_N(DIN_N), .DOUT_N(DOUT_N)) roi (
        .clk(clk),
        .din(din), .dout(dout));
endmodule

module roi(input clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = 4;
    parameter DOUT_N = 4;

    genvar i;
    generate
        //CLK
        (* KEEP, DONT_TOUCH *)
        reg clk_reg;
        always @(posedge clk) begin
            clk_reg <= clk_reg;
        end

        //DIN
        for (i = 0; i < DIN_N; i = i+1) begin:ins
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                .INIT(64'b01)
            ) lut (
                .I0(din[i]),
                .I1(1'b0),
                .I2(1'b0),
                .I3(1'b0),
                .I4(1'b0),
                .I5(1'b0),
                .O());
        end

        //DOUT
        for (i = 0; i < DOUT_N; i = i+1) begin:outs
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                .INIT(64'b01)
            ) lut (
                .I0(1'b0),
                .I1(1'b0),
                .I2(1'b0),
                .I3(1'b0),
                .I4(1'b0),
                .I5(1'b0),
                .O(dout[i]));
        end
    endgenerate
endmodule
