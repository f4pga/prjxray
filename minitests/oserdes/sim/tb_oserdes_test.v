`include "../src/oserdes_test.v"
`include "../src/lfsr.v"
`include "../src/comparator.v"

`default_nettype none
`timescale 1ns / 1ps

// ============================================================================

module tb;

// ============================================================================

reg CLK;
initial CLK <= 1'b0;
always #0.5 CLK <= !CLK;

reg [3:0] rst_sr;
initial rst_sr <= 4'hF;
always @(posedge CLK) rst_sr <= rst_sr >> 1;
wire RST;
assign RST = rst_sr[0];

// ============================================================================

initial begin
    $dumpfile("waveforms.vcd");
    $dumpvars;
end

integer cycle_cnt;
initial cycle_cnt <= 0;

always @(posedge CLK)
    if (!RST) cycle_cnt <= cycle_cnt + 1;

always @(posedge CLK)
    if (!RST && cycle_cnt >= 10000)
        $finish;

// ============================================================================

reg clk_r;
always @(posedge CLK)
    if (RST) clk_r <= 1'b0;
    else     clk_r <= !clk_r;

wire CLK1 = CLK;
wire CLK2 = clk_r;

// ============================================================================
wire s_dat;

oserdes_test #
(
.DATA_WIDTH (8),
.DATA_RATE  ("SDR"),
.ERROR_HOLD (4)
)
trx_path
(
.CLK    (CLK),
.CLK1   (CLK1),
.CLK2   (CLK2),
.RST    (RST),

.IO_DAT (s_dat)
);

endmodule

