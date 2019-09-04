`default_nettype none
`timescale 1ns / 1ps

`include "../src/message_formatter.v"

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
    if (!RST && cycle_cnt >= 150)
        $finish;

// ============================================================================

wire i_stb = (cycle_cnt == 10);
wire [32*2-1:0] i_dat = 64'h01234567_ABCD4321;

wire o_stb;
wire [7:0] o_dat;

message_formatter #
(
.WIDTH          (32),
.COUNT          (2),
.TX_INTERVAL    (4)
)
dut
(
.CLK    (CLK),
.RST    (RST),

.I_STB  (i_stb),
.I_DAT  (i_dat),

.O_STB  (o_stb),
.O_DAT  (o_dat)
);

always @(posedge CLK)
    if (o_stb)
        $display("%c", o_dat);

endmodule

