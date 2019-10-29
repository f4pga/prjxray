`include "src/plle2_test.v"

`default_nettype none

// ============================================================================

module top
(
input  wire clk,

input  wire rx,
output wire tx,

input  wire [15:0] sw,
output wire [15:0] led
);

// ============================================================================

assign tx = rx;

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
// The tester

plle2_test plle2_test
(
.CLK    (CLK),
.RST    (RST),

.I_CLKINSEL (sw[1]),

.O_LOCKED   (led[15]),
.O_CNT      (led[5:0])
);

assign led [14]   = |sw;
assign led [13:6] = 0;

endmodule

