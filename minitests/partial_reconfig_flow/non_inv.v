//Connect the switches to the LEDs, inverting the signal in the ROI
//Assumes # inputs = # outputs

`include "defines.v"

module roi(input clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;
    wire [DIN_N-1:0] internal;

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
            //Very expensive inverter
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                .INIT(64'b10)
            ) lut (
                .I0(din[i]),
                .I1(1'b0),
                .I2(1'b0),
                .I3(1'b0),
                .I4(1'b0),
                .I5(1'b0),
                .O(internal[i]));
        end

        //DOUT
        for (i = 0; i < DOUT_N; i = i+1) begin:outs
            //Very expensive buffer
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                .INIT(64'b010)
            ) lut (
                .I0(internal[i]),
                .I1(1'b0),
                .I2(1'b0),
                .I3(1'b0),
                .I4(1'b0),
                .I5(1'b0),
                .O(dout[i]));
        end
    endgenerate
endmodule
