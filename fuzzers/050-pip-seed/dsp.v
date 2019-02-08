`include "setseed.vh"

module dsp(input clk, input [(INCR_LUT_OUT_WIDTH+1)*8-1:0] din, output [127:0] dout);
    parameter integer INCR_LUT_OUT_WIDTH = 0;
    localparam integer N = 5;
    localparam integer N_OUT =
             `SEED % 3 == 2 ? 128 :
             `SEED % 3 == 1 ? 256 : 512;

    wire [N*4*48-1:0] dsp_out;

    assign dout = dsp_out[N_OUT-1:N_OUT-128];

    genvar i;
    generate
        for (i = 0; i < N; i = i+1) begin:is
            (* KEEP, DONT_TOUCH *)
            DSP48E1 #(
                .USE_DPORT("TRUE")
            ) dsp (
                .P(dsp_out[i*48*4+48-1:i*48*4]),
                .CLK(clk),
                .A(din[29:0]),
                .B(din[47:30]),
                .C(din[95:48]),
                .D(din[120:96]),
                .RSTA(din[121]),
                .RSTB(din[122]),
                .RSTC(din[123]),
                .RSTCTRL(din[124]),
                .RSTD(din[125]),
                .RSTINMODE(din[126]),
                .RSTM(din[127]),
                .ACIN(din[157:128]),
                .BCIN(din[175:158])
            );

            (* KEEP, DONT_TOUCH *)
            DSP48E1 #(
                .USE_DPORT("TRUE")
            ) dsp_const (
                .P(dsp_out[i*48*4+48*2-1:i*48*4+48]),
                .CLK(clk),
                .A(din[29:0]),
                .B(din[47:30]),
                .C(din[95:48]),
                .D()
            );

            (* KEEP, DONT_TOUCH *)
            DSP48E1 #(
                .USE_DPORT("TRUE")
            ) dsp_const_0 (
                .P(dsp_out[i*48*4+48*3-1:i*48*4+48*2]),
                .CLK(clk),
                .A(din[29:0]),
                .B(din[47:30]),
                .C(din[95:48]),
                .D(0)
            );

            (* KEEP, DONT_TOUCH *)
            DSP48E1 #(
                .USE_DPORT("TRUE")
            ) dsp_const_1 (
                .P(dsp_out[i*48*4+48*4-1:i*48*4+48*3]),
                .CLK(clk),
                .A(din[29:0]),
                .B(din[47:30]),
                .C(din[95:48]),
                .D(1)
            );
        end
    endgenerate
endmodule

