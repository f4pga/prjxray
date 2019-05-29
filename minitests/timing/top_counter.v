module top(input clk, stb, di, output do);

reg [31:0] counter = 0;

assign do = &counter;

always @(posedge clk) begin
    counter <= counter + 1;
end

endmodule
