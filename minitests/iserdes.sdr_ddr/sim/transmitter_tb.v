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
    if (!RST && cycle_cnt >= 100)
        $finish;

// ============================================================================
wire o_stb;
wire [7:0] o_dat;

wire s_clk;
wire s_ce;
wire s_dat;

transmitter #
(
.WIDTH  (8),
.MODE   ("SDR")
)
transmitter
(
.CLK    (CLK),
.RST    (RST),

.O_STB  (o_stb),
.O_DAT  (o_dat),

.S_CLK  (s_clk),
.S_CE   (s_ce),
.S_DAT  (s_dat)
);

endmodule
