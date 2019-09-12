`include "../src/rom.v"
`include "../src/serializer.v"
`include "../src/transmitter.v"
`include "../src/receiver.v"
`include "../src/comparator.v"
`include "../src/trx_path.v"

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
wire s_dat;

trx_path #
(
.WIDTH  (8),
.MODE   ("SDR")
)
trx_path
(
.CLK    (CLK),
.RST    (RST),

.O_DAT  (s_dat),
.I_DAT  (s_dat)
);

endmodule

