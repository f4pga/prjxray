//See README and tcl for more info

`default_nettype none

`include "defines.v"

module roi(input wire clk,
        input wire [DIN_N-1:0] din, output wire [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    wire [DIN_N-1:0] din_lut;
    wire [DOUT_N-1:0] dout_lut;

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
                .O(din_lut[i]));
        end

        //DOUT
        for (i = 0; i < DOUT_N; i = i+1) begin:outs
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                .INIT(64'b01)
            ) lut (
                .I0(dout_lut[i]),
                .I1(1'b0),
                .I2(1'b0),
                .I3(1'b0),
                .I4(1'b0),
                .I5(1'b0),
                .O(dout[i]));
        end
    endgenerate

    demoscene demoscene(.clk(clk), .din(din_lut), .dout(dout_lut));
endmodule

module demoscene(input wire clk,
        input wire [DIN_N-1:0] din, output wire [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    //assign dout = 8'b10101010;
    demoscene_scroll dut(.clk(clk), .din(din), .dout(dout));
endmodule

/*
Leftmost LED counts at one second
*/
module demoscene_counter(input wire clk,
        input wire [DIN_N-1:0] din, output wire [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;
    /*
    100 MHz clock
    Lets get MSB to 1 second
    Need 27 bits
    In [3]: math.log(100e6, 2)
    Out[3]: 26.5754247590989
    */
    reg [26:0] div;
    always @(posedge clk) begin
        div <= div + 1'b1;
    end
    assign dout = div[26:19];
endmodule

//Loosely based on http://www.asic-world.com/code/hdl_models/lfsr.v
module lfsr(input wire clk, output wire dout);
    reg [7:0] out = 8'hAA;
    wire feedback = !(out[7] ^ out[3]);

    always @(posedge clk) begin
        out <= {out[6],out[5],
              out[4],out[3],
              out[2],out[1],
              out[0], feedback};
    end
    assign dout = out[0];
endmodule

// http://www.fpga4fun.com/Counters3.html
module lfsr2(input wire clk, output wire dout);
    reg [7:0] LFSR = 255;
    wire feedback = LFSR[7];
    assign dout = LFSR[0];

    always @(posedge clk) begin
      LFSR[0] <= feedback;
      LFSR[1] <= LFSR[0];
      LFSR[2] <= LFSR[1] ^ feedback;
      LFSR[3] <= LFSR[2] ^ feedback;
      LFSR[4] <= LFSR[3] ^ feedback;
      LFSR[5] <= LFSR[4];
      LFSR[6] <= LFSR[5];
      LFSR[7] <= LFSR[6];
    end
endmodule
/*
Scrolls an LSFR across
*/
module demoscene_scroll(input wire clk,
        input wire [DIN_N-1:0] din, output wire [DOUT_N-1:0] dout);
    parameter DIN_N = `DIN_N;
    parameter DOUT_N = `DOUT_N;

    reg [26:0] div;
    always @(posedge clk) begin
        div <= div + 1'b1;
    end

    wire randbit;
    lfsr2 lfsr(.clk(clk), .dout(randbit));

    reg [7:0] leds = 8'hCC;
    reg last;
    reg tick;
    always @(posedge clk) begin
        last <= div[23];
        tick <= div[23] ^ last;

        if (tick) begin
            leds = {leds, randbit};
        end
    end

    assign dout = leds;
endmodule

