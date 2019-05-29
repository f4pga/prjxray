module top(input clk, stb, di, output do);

wire [5:0] I;
wire LUT_O;
wire FF_Q;

localparam SIG_MASK = `SIG_MASK;

genvar i;
generate for(i = 0; i < 6; i = i + 1) begin : loop
    if(((1 << i) & SIG_MASK) != 0) begin
        assign I[i] = FF_Q;
    end else begin
        assign I[i] = 1;
    end
end endgenerate

(* LOC="SLICE_X37Y74", BEL="B6LUT", KEEP, DONT_TOUCH *)
LUT6 lut(
    .I0(I[0]),
    .I1(I[1]),
    .I2(I[2]),
    .I3(I[3]),
    .I4(I[4]),
    .I5(I[5]),
    .O(LUT_O)
);

(* LOC="SLICE_X37Y74", BEL="BFF", KEEP, DONT_TOUCH *)
FDRE ff(
    .C(clk),
    .R(0),
    .CE(1),
    .D(LUT_O),
    .Q(FF_Q)
);

endmodule
