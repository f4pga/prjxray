module dsp(input clk, input [127:0] din, output dout);
    localparam integer N = 5;

    wire [N*3*48-1:0] dsp_out;

    assign dout = | dsp_out;

    genvar i;
    generate
        for (i = 0; i < N; i = i+1) begin:is
            (* KEEP, DONT_TOUCH *)
            DSP48E1 #(
                .USE_DPORT("TRUE")
            ) dsp (
                .P(dsp_out[i*48*3+48-1:i*48*3]),
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
                .RSTM(din[127])
            );

            (* KEEP, DONT_TOUCH *)
            DSP48E1 #(
                .USE_DPORT("TRUE")
            ) dsp_const (
                .P(dsp_out[i*48*3+48*2-1:i*48*3+48]),
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
                .P(dsp_out[i*48*3+48*3-1:i*48*3+48*2]),
                .CLK(clk),
                .A(din[29:0]),
                .B(din[47:30]),
                .C(din[95:48]),
                .D(0)
            );
        end
    endgenerate
endmodule

