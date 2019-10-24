`include "src/lfsr.v"
`include "src/oserdes_test.v"
`include "src/comparator.v"

`default_nettype none

// ============================================================================

module top
(
input  wire clk,

input  wire rx,
output wire tx,

input  wire [15:0] sw,
output wire [15:0] led,

inout  wire [9:0]  io
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
// Clocks for OSERDES

wire CLK1_X0Y0;
wire CLK2_X0Y0;

wire CLK1_X0Y2;
wire CLK2_X0Y2;

wire CLK1_X1Y1;
wire CLK2_X1Y1;

reg clk_r;
always @(posedge CLK)
    if (RST) clk_r <= 1'b0;
    else     clk_r <= !clk_r;

BUFMR mr_buf_x1y1_1 (.I(CLK),   .O(CLK1_X1Y1));
BUFMR mr_buf_x1y1_2 (.I(clk_r), .O(CLK2_X1Y1));

BUFMR mr_buf_x0y2_1 (.I(CLK),   .O(CLK1_X0Y2));
BUFMR mr_buf_x0y2_2 (.I(clk_r), .O(CLK2_X0Y2));

BUFMR mr_buf_x0y0_1 (.I(CLK),   .O(CLK1_X0Y0));
BUFMR mr_buf_x0y0_2 (.I(clk_r), .O(CLK2_X0Y0));

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

  wire CLK1 = (i >= 0 && i < 4) ? CLK1_X1Y1 :
              (i >= 4 && i < 7) ? CLK1_X0Y2 :
                                  CLK1_X0Y0;

  wire CLK2 = (i >= 0 && i < 4) ? CLK2_X1Y1 :
              (i >= 4 && i < 7) ? CLK2_X0Y2 :
                                  CLK2_X0Y0;

  oserdes_test #
  (
  .DATA_WIDTH   (DATA_WIDTH),
  .DATA_RATE    (DATA_RATE)
  )
  oserdes_test
  (
  .CLK      (CLK),
  .CLK1     (CLK1),
  .CLK2     (CLK2),
  .RST      (RST),

  .IO_DAT   (io[i]),
  .O_ERROR  (error[i])
  );

end endgenerate

// ============================================================================
// IOs
reg [24:0] heartbeat_cnt;

always @(posedge CLK)
    heartbeat_cnt <= heartbeat_cnt + 1;

assign led[ 0] = !error[0];
assign led[ 1] = !error[1];
assign led[ 2] = !error[2];
assign led[ 3] = !error[3];
assign led[ 4] = !error[4];
assign led[ 5] = !error[5];
assign led[ 6] = !error[6];
assign led[ 7] = !error[7];
assign led[ 8] = !error[8];
assign led[ 9] = !error[9];
assign led[10] = heartbeat_cnt[23];
assign led[11] = 1'b0;
assign led[12] = 1'b0;
assign led[13] = 1'b0;
assign led[14] = 1'b0;
assign led[15] = 1'b0;

endmodule

