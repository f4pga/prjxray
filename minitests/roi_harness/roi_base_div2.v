//See README and tcl for more info

`include "defines.v"

module roi(input clk,
        input [DIN_N-1:0] din, output [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    wire div_clk;
    wire clk_IBUF_BUFG;
    BUFR #(
        .BUFR_DIVIDE(2)
    ) clock_divider (
        .I(clk),
        .O(div_clk),
        .CE(1),
        .CLR(0)
    );

    BUFG clock_buffer (
        .I(div_clk),
        .O(clk_IBUF_BUFG)
    );

    genvar i;
    generate
        //CLK
        (* KEEP, DONT_TOUCH *)
        reg clk_reg;
        always @(posedge clk_IBUF_BUFG) begin
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
