// Copyright (C) 2017-2020  The Project X-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

module idelay_histogram #
(
parameter UART_PRESCALER = 868   // UART prescaler
)
(
// Closk & reset
input  wire CLK,
input  wire RST,

// UART
input  wire UART_RX,
output wire UART_TX,

// TEST - internal loopback
input  wire TEST,

// Input and output pins
output wire O,
input  wire I,

output wire REF_O,
output wire REF_I,

// IDELAY delay setting output
output wire [4:0] DELAY
);

// ============================================================================
// Data generator
reg [1:0] ce_cnt;
wire ce;

always @(posedge CLK)
    ce_cnt <= ce_cnt + 1;

assign ce = (ce_cnt == 0);

// LFSR
wire [15:0] lfsr_r;

lfsr lfsr
(
.clk    (CLK),
.rst    (RST),
.ce     (ce),
.r      (lfsr_r)
);

reg  o_stb;
wire o_dat;

always @(posedge CLK)
    if (RST)
        o_stb <= 1'b0;
    else
        o_stb <= ce;

assign o_dat = lfsr_r[0];
assign O     = o_dat;

// ============================================================================
// Data input with IDELAY
wire dly_dat;
wire dly_ld;
wire [5:0] dly_cnt;

IDELAYE2 #
(
.IDELAY_TYPE    ("VAR_LOAD"),
.DELAY_SRC      ("IDATAIN")
)
idelay
(
.IDATAIN    (I),
.DATAOUT    (dly_dat),

.C          (CLK),
.LD         (dly_ld),
.CNTVALUEIN (dly_cnt),
.CNTVALUEOUT(DELAY)
);

assign OI = dly_dat;

// ============================================================================
// Data comparator
reg o_dat_r;

reg cmp_s0_stb;
reg cmp_s0_o_dat;
reg cmp_s0_i_dat;

reg cmp_s1_stb;
reg cmp_s1_err;

always @(posedge CLK)
    o_dat_r <= o_dat;

always @(posedge CLK)
    if (RST)
        cmp_s0_stb <= 1'b0;
    else
        cmp_s0_stb <= o_stb;

always @(posedge CLK)
    if (o_stb)
        cmp_s0_o_dat <= o_dat_r;
always @(posedge CLK)
    if (o_stb)
        cmp_s0_i_dat <= (TEST) ? O : dly_dat;


always @(posedge CLK)
    if (RST)
        cmp_s1_stb <= 1'b0;
    else
        cmp_s1_stb <= cmp_s0_stb;

always @(posedge CLK)
    cmp_s1_err <= cmp_s0_o_dat ^ cmp_s0_i_dat;

assign REF_O = o_dat_r;
assign REF_I = dly_dat;

// ============================================================================
// Error counter
wire             cnt_stb;
wire [32*24-1:0] cnt_dat;

error_counter #
(
.COUNT_WIDTH (24),
.DELAY_TAPS  (32),

.TRIGGER_INTERVAL   (50000000),
.HOLDOFF_TIME       (100),
.MEASURE_TIME       (10000)
)
error_counter
(
.CLK    (CLK),
.RST    (RST),

.I_STB  (cmp_s1_stb),
.I_ERR  (cmp_s1_err),

.DLY_LD (dly_ld),
.DLY_CNT(dly_cnt),

.O_STB  (cnt_stb),
.O_DAT  (cnt_dat)
);

// ============================================================================
// Message formatter
wire        uart_x_stb;
wire [7:0]  uart_x_dat;

message_formatter #
(
.WIDTH       (24),
.COUNT       (32),
.TX_INTERVAL (UART_PRESCALER * 11) // 10 bits plus one more.
)
message_formatter
(
.CLK    (CLK),
.RST    (RST),

.I_STB  (cnt_stb),
.I_DAT  (cnt_dat),

.O_STB  (uart_x_stb),
.O_DAT  (uart_x_dat)
);

// ============================================================================
// UART

// Baudrate prescaler initializer
reg  [7:0]  reg_div_we_sr;
wire        reg_div_we;

always @(posedge CLK)
    if (RST)    reg_div_we_sr <= 8'h01;
    else        reg_div_we_sr <= {reg_div_we_sr[6:0], 1'd0};

assign reg_div_we = reg_div_we_sr[7];

// The UART
simpleuart uart
(
.clk            (CLK),
.resetn         (!RST),

.ser_rx         (UART_RX),
.ser_tx         (UART_TX),

.reg_div_we     ({reg_div_we, reg_div_we, reg_div_we, reg_div_we}),
.reg_div_di     (UART_PRESCALER),
.reg_div_do     (),

.reg_dat_we     (uart_x_stb),
.reg_dat_re     (1'd0),
.reg_dat_di     ({24'd0, uart_x_dat}),
.reg_dat_do     (),
.reg_dat_wait   ()
);

// Debug
always @(posedge CLK)
    if (uart_x_stb)
        $display("%c", uart_x_dat);

endmodule

