`default_nettype none
`timescale 1ns / 1ps

`include "../src/iserdes_idelay_histogram.v"
`include "../src/idelay_calibrator.v"
`include "../src/error_counter.v"
`include "../src/message_formatter.v"
`include "../src/lfsr.v"
`include "../src/simpleuart.v"

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
    if (!RST && cycle_cnt >= 5000)
        $finish;

// ============================================================================
wire dat_o;
reg  dat_i;

always @(*) dat_i <= #1.1 dat_o;

iserdes_idelay_histogram #
(
)
dut
(
.CLK        (CLK),
.RST        (RST),

.UART_RX    (1'b1),
.UART_TX    (),

.O          (dat_o),
.I          (dat_i)
);

endmodule

