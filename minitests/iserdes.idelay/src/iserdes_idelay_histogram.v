// ============================================================================

module iserdes_idelay_histogram #
(
parameter UART_PRESCALER = 868,  // UART prescaler
parameter ISERDES_MODE   = "DDR",
parameter ISERDES_WIDTH  = 8
)
(
// Closk & reset
input  wire CLK,
input  wire RST,

// UART
input  wire UART_RX,
output wire UART_TX,

// Input and output pins
output wire O,
input  wire I,

// Signals at the input of the comparator (for monitoring)
output wire REF_O,
output wire REF_I,
output wire REF_C,

// IDELAY delay setting output
output wire [4:0] DELAY
);

// ============================================================================
// Data generator

// Serialized data clock generator
reg [2:0] ce_cnt;
wire      ce_x2_p;
wire      ce_x2_n;
wire      ce_x1_p;
wire      ce_x1_n;

initial ce_cnt <= 0;
always @(posedge CLK)
    ce_cnt <= ce_cnt + 1;

assign ce_x2_p = (ce_cnt[0:0] == 0) && !ce_cnt[1];
assign ce_x2_n = (ce_cnt[0:0] == 0) &&  ce_cnt[1];

assign ce_x1_p = (ce_cnt[1:0] == 0) && !ce_cnt[2];
assign ce_x1_n = (ce_cnt[1:0] == 0) &&  ce_cnt[2];

// LFSR
wire [15:0] lfsr_r;

lfsr lfsr
(
.clk    (CLK),
.rst    (RST),
.ce     ((ISERDES_MODE == "SDR") ? ce_x1_p : ce_x2_p),
.r      (lfsr_r)
);

// Data serializer
reg  o_clk;
reg  o_stb;
wire o_dat;

always @(posedge CLK)
    if (RST)
        o_clk <= 1'b0;
    else if (ce_x1_p)
        o_clk <= 1'b1;
    else if (ce_x1_n)
        o_clk <= 1'b0;

always @(posedge CLK)
    if (RST)
        o_stb <= 1'b0;
    else begin
        if (ISERDES_MODE == "SDR")
            o_stb <= ce_x1_p;
        else if (ISERDES_MODE == "DDR")
            o_stb <= ce_x2_p;
    end

assign o_dat = lfsr_r[0];

// Output the data, the clock is routed internally.
assign O = o_dat;

// ============================================================================
// Data input with IDELAY and ISERDES
wire dly_dat;
wire dly_ld;
wire [4:0] dly_cnt;

wire [7:0] ser_dat;
wire       ser_dat_ref;
wire       ser_rst;
reg        ser_clk;
wire       ser_clkdiv;

// Delay the ISERDES clock by 1 CLK. This aligns serialized clock and data
// edges and allow to expose influende of differend IDELAY settings.
always @(posedge CLK)
    ser_clk <= o_clk;

// ISERDES reset generator (required for it to work properly!)
reg [3:0]  ser_rst_sr;
initial    ser_rst_sr <= 4'hF;

always @(posedge ser_clkdiv or posedge RST)
    if (RST) ser_rst_sr <= 4'hF;
    else     ser_rst_sr <= ser_rst_sr >> 1;

assign ser_rst = ser_rst_sr[0];

// BUFR - generation of CLKDIV
localparam DIVIDE = (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 2) ? "2" :
                    (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 3) ? "3" :
                    (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 4) ? "4" :
                    (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 5) ? "5" :
                    (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 6) ? "6" :
                    (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 7) ? "7" :
                    (ISERDES_MODE == "SDR" && ISERDES_WIDTH == 8) ? "8" :

                    (ISERDES_MODE == "DDR" && ISERDES_WIDTH == 4) ? "2" :
                    (ISERDES_MODE == "DDR" && ISERDES_WIDTH == 6) ? "3" :
                    (ISERDES_MODE == "DDR" && ISERDES_WIDTH == 8) ? "4" : "BYPASS";
BUFR #
(
.BUFR_DIVIDE    (DIVIDE)
)
bufr
(
.I      (ser_clk),
.O      (ser_clkdiv),
.CLR    (RST),
.CE     (1'd1)
);

// IDELAY
IDELAYE2 #
(
.IDELAY_TYPE    ("VAR_LOAD"),
.DELAY_SRC      ("IDATAIN")
)
idelay
(
.IDATAIN        (I),
.DATAOUT        (dly_dat),

.C              (CLK),
.LD             (dly_ld),
.CNTVALUEIN     (dly_cnt),
.CNTVALUEOUT    (DELAY)
);

// ISERDES
ISERDESE2 #
(
.DATA_RATE          (ISERDES_MODE),
.DATA_WIDTH         (ISERDES_WIDTH),
.INTERFACE_TYPE     ("NETWORKING"),
.NUM_CE             (1),
.IOBDELAY           ("BOTH"),
.IS_CLKB_INVERTED   (1)
)
iserdes
(
.DDLY       (dly_dat),
.O          (ser_dat_ref),
.Q1         (ser_dat[0]),
.Q2         (ser_dat[1]),
.Q3         (ser_dat[2]),
.Q4         (ser_dat[3]),
.Q5         (ser_dat[4]),
.Q6         (ser_dat[5]),
.Q7         (ser_dat[6]),
.Q8         (ser_dat[7]),
.CLK        (ser_clk),
.CLKB       (ser_clk),
.CLKDIV     (ser_clkdiv),
.CE1        (1'b1),
.RST        (ser_rst),
.BITSLIP    (1'b0)
);

// ============================================================================
// Data serializer

// ISERDES clock edge detector
reg ser_clk_r;
reg ser_clkdiv_r;

always @(posedge CLK)
    ser_clk_r <= ser_clk;
always @(posedge CLK)
    ser_clkdiv_r <= ser_clkdiv;

wire ser_clk_e = (ISERDES_MODE == "SDR") ? (ser_clk && !ser_clk_r) :
                 (ISERDES_MODE == "DDR") ? (ser_clk ^   ser_clk_r) : 0;

wire ser_clkdiv_e = ser_clkdiv && !ser_clkdiv_r;

// Data serializer
reg [7:0] ser2_sr;
wire      ser2_stb;
wire      ser2_dat;

always @(posedge CLK)
    if (ser_clk_e && ser_clkdiv_e)
        ser2_sr <= ser_dat;
    else if (ser_clk_e)
        ser2_sr <= ser2_sr << 1;

assign ser2_stb = ser_clk_e;
assign ser2_dat = ser2_sr[ISERDES_WIDTH-1];

// ============================================================================
// Output data delay needed to compensate ISERDES latency
reg [23:0] bit_sr;
reg        bit_stb;
wire       bit_dat;

always @(posedge CLK)
    bit_stb <= o_stb;
always @(posedge CLK)
    if (o_stb) bit_sr <= (bit_sr << 1) | o_dat;

localparam BIT_DELAY = (ISERDES_MODE == "SDR") ? (ISERDES_WIDTH * 2 - 2) :
                     /*(ISERDES_MODE == "DDR")*/ (ISERDES_WIDTH + 4);

assign bit_dat = bit_sr[BIT_DELAY];

// ============================================================================
// Data comparator
reg cmp_s0_stb;
reg cmp_s0_o_dat;
reg cmp_s0_i_dat;

reg cmp_s1_stb;
reg cmp_s1_err;

always @(posedge CLK)
    if (RST)
        cmp_s0_stb <= 1'b0;
    else
        cmp_s0_stb <= bit_stb;

always @(posedge CLK)
    if (o_stb)
        cmp_s0_o_dat <= bit_dat;
always @(posedge CLK)
    if (o_stb)
        cmp_s0_i_dat <= ser2_dat;


always @(posedge CLK)
    if (RST)
        cmp_s1_stb <= 1'b0;
    else
        cmp_s1_stb <= cmp_s0_stb;

always @(posedge CLK)
    cmp_s1_err <= cmp_s0_o_dat ^ cmp_s0_i_dat;


reg o_dat_r;

always @(posedge CLK)
    o_dat_r <= o_dat;

// Reference output
assign REF_O = o_dat_r;
assign REF_I = ser_dat_ref;
assign REF_C = ser_clk;

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

