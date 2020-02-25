module top (
    input  wire clk,

    input  wire [7:0] sw,
    output wire [7:0] led
);
    assign led = sw;
endmodule
