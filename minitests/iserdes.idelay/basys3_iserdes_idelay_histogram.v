`include "src/iserdes_idelay_histogram.v"
`include "src/idelay_calibrator.v"
`include "src/error_counter.v"
`include "src/message_formatter.v"
`include "src/lfsr.v"
`include "src/simpleuart.v"

`default_nettype none

// ============================================================================

module top
(
input  wire clk,

input  wire rx,
output wire tx,

input  wire [15:0] sw,
output wire [15:0] led,

output wire ja1,
output wire ja2,
output wire ja3,
output wire ja4,
output wire ja7,
output wire ja8,
output wire ja9,
output wire ja10,

output wire jb1,
output wire jb2,
output wire jb3,
output wire jb4,
output wire jb7,
output wire jb8,
output wire jb9,
output wire jb10,

output wire jc1,
output wire jc2,
output wire jc3,
output wire jc4,
output wire jc7,
output wire jc8,
output wire jc9,
output wire jc10,

output wire xadc1_p,
output wire xadc2_p,
output wire xadc3_p,
output wire xadc4_p,
input  wire xadc1_n,
output wire xadc2_n,
output wire xadc3_n,
output wire xadc4_n
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

wire pll_clkfb;
wire pll_locked;

wire CLK100;
wire CLK200;
wire CLK400;

PLLE2_BASE #
(
.CLKFBOUT_MULT  (8),
.CLKOUT0_DIVIDE (8),
.CLKOUT1_DIVIDE (4)
)
pll
(
.CLKIN1     (clk),

.CLKFBIN    (pll_clkfb),
.CLKFBOUT   (pll_clkfb),

.CLKOUT0    (CLK100),
.CLKOUT1    (CLK200),

.RST        (rst_sr[0]),
.LOCKED     (pll_locked)
);

// ============================================================================
// IDELAY calibrator
wire cal_rdy;

idelay_calibrator cal
(
.refclk (CLK100),
.rst    (rst_sr[0] || !pll_locked),
.rdy    (cal_rdy)
);

wire RST = rst_sr[0] || !cal_rdy;

// ============================================================================
wire sig_out;
wire sig_inp;
wire [4:0] delay;

wire sig_ref_i;
wire sig_ref_o;
wire sig_ref_c;

iserdes_idelay_histogram #
(
.UART_PRESCALER (868)
)
iserdes_idelay_histogram
(
.CLK        (CLK100),
.RST        (RST),

.UART_RX    (rx),
.UART_TX    (tx),

.O          (sig_out),
.I          (sig_inp),

.REF_O      (sig_ref_o),
.REF_I      (sig_ref_i),
.REF_C      (sig_ref_c),

.DELAY      (delay)
);

// ============================================================================
// I/O connections
reg [23:0] heartbeat_cnt;

always @(posedge CLK100)
    heartbeat_cnt <= heartbeat_cnt + 1;

assign led[ 0] = heartbeat_cnt[23];
assign led[ 1] = cal_rdy;
assign led[ 2] = 1'b0;
assign led[ 3] = 1'b0;
assign led[ 4] = 1'b0;
assign led[ 5] = 1'b0;
assign led[ 6] = 1'b0;
assign led[ 7] = 1'b0;
assign led[ 8] = 1'b0;
assign led[ 9] = 1'b0;
assign led[10] = 1'b0;
assign led[11] = delay[0];
assign led[12] = delay[1];
assign led[13] = delay[2];
assign led[14] = delay[3];
assign led[15] = delay[4];

assign ja1  = 1'b0;
assign ja2  = 1'b0;
assign ja3  = 1'b0;
assign ja4  = 1'b0;
assign ja7  = 1'b0;
assign ja8  = 1'b0;
assign ja9  = 1'b0;
assign ja10 = 1'b0;

assign jb1  = 1'b0;
assign jb2  = 1'b0;
assign jb3  = 1'b0;
assign jb4  = 1'b0;
assign jb7  = 1'b0;
assign jb8  = 1'b0;
assign jb9  = 1'b0;
assign jb10 = 1'b0;

assign jc1  = 1'b0;
assign jc2  = 1'b0;
assign jc3  = 1'b0;
assign jc4  = 1'b0;
assign jc7  = 1'b0;
assign jc8  = 1'b0;
assign jc9  = 1'b0;
assign jc10 = 1'b0;

assign xadc1_p = sig_ref_i;
assign xadc2_p = sig_ref_o;
assign xadc3_p = sig_ref_c;
assign xadc4_p = 1'b0;
//assign xadc1_n = 1'b0;
assign xadc2_n = sig_out;
assign xadc3_n = 1'b0;
assign xadc4_n = 1'b0;

assign sig_inp = xadc1_n;

endmodule
