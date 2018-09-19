module top(input clk, stb, di, output do);
    reg dor;
	always @(posedge clk) begin
	    dor <= stb & di;
	end
    assign do = dor;
endmodule

