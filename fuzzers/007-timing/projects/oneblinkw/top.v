module roi (
        input wire clk,
        output wire out);
    reg [23:0] counter;
    assign out = counter[23] ^ counter[22] ^ counter[2] && counter[1] || counter[0];

    always @(posedge clk) begin
        counter <= counter + 1;
    end
endmodule

module top(input wire clk, input wire stb, input wire di, output wire do);
    localparam integer DIN_N = 0;
    localparam integer DOUT_N = 1;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];
    roi roi(
            .clk(clk),
            .out(dout[0])
            );
endmodule

