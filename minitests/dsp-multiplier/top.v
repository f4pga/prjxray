module top (
    input wire clk,
    input wire [17:0] a,
    input wire [17:0] b,
    output wire [35:0] p
);

    // Instantiate the DSP48E1 primitive
    DSP48E1 #(
        .A_INPUT("DIRECT"),
        .B_INPUT("DIRECT"),
        .USE_DPORT("FALSE"),
        .USE_MULT("MULTIPLY"),
        .USE_SIMD("ONE48")
    ) dsp48e1_inst (
        .CLK(clk),
        .A(a),
        .B(b),
        .P(p)
    );

endmodule
