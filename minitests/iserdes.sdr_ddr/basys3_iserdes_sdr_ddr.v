`include "src/rom.v"
`include "src/serializer.v"
`include "src/transmitter.v"
`include "src/receiver.v"
`include "src/comparator.v"
`include "src/iserdes_sdr_ddr_test.v"

`default_nettype none

// ============================================================================

module top
(
input  wire clk,

input  wire rx,
output wire tx,

input  wire [15:0] sw,
output wire [15:0] led,

inout  wire [9:0] io
);

// ============================================================================
// Clock & reset
reg [3:0] rst_sr;

initial rst_sr <= 4'hF;

always @(posedge clk)
    if (sw[0])
        rst_sr <= 4'hF;
    else
        rst_sr <= rst_sr >> 1;

wire CLK = clk;
wire RST = rst_sr[0];

// ============================================================================
// Test uints
wire [9:0] error;

genvar i;
generate for (i=0; i<10; i=i+1) begin

  localparam DATA_WIDTH = (i == 0) ?   2 :
                          (i == 1) ?   3 :
                          (i == 2) ?   4 :
                          (i == 3) ?   5 :
                          (i == 4) ?   6 :
                          (i == 5) ?   7 :
                          (i == 6) ?   8 :
                          (i == 7) ?   4 :
                          (i == 8) ?   6 :
                        /*(i == 9) ?*/ 8;

  localparam DATA_RATE =  (i <  7) ? "SDR" : "DDR";

  iserdes_sdr_ddr_test #
  (
  .DATA_WIDTH   (DATA_WIDTH),
  .DATA_RATE    (DATA_RATE)
  )
  iserdes_test
  (
  .CLK      (CLK),
  .RST      (RST),

  .IO_DAT   (io[i]),
  .O_ERROR  (error[i])
  );

end endgenerate

// ============================================================================
// I/O connections

reg [23:0] heartbeat_cnt;

always @(posedge CLK)
    heartbeat_cnt <= heartbeat_cnt + 1;


assign led[9:  0] = (RST) ? 9'd0 : ~error;
assign led[   10] = heartbeat_cnt[22];
assign led[15:11] = 0;

endmodule
