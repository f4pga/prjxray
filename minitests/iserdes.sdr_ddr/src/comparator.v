`default_nettype none

// ============================================================================

module comparator #
(
parameter WIDTH = 8,
parameter ERROR_COUNT = 8,
parameter ERROR_HOLD = 2500000
)
(
// Clock and reset
input  wire CLK,
input  wire RST,

// Transmitted data input port
input  wire             TX_STB,
input  wire [WIDTH-1:0] TX_DAT,

// Received data input port + bitslip
input  wire             RX_STB,
input  wire [WIDTH-1:0] RX_DAT,
output wire             RX_BITSLIP,

// Error indicator
output wire             O_ERROR
);

// ============================================================================
// Data latch and comparator
reg [WIDTH-1:0] tx_dat;
reg             tx_valid;

reg [WIDTH-1:0] rx_dat;
reg             rx_valid;

wire i_rdy = rx_valid && rx_valid;

always @(posedge CLK)
    if (!tx_valid && TX_STB)
        tx_dat <= TX_DAT;

always @(posedge CLK)
    if (RST)
        tx_valid <= 1'b0;
    else if (i_rdy)
        tx_valid <= 1'b0;
    else if (TX_STB)
        tx_valid <= 1'b1;

always @(posedge CLK)
    if (!rx_valid && RX_STB)
        rx_dat <= RX_DAT;

always @(posedge CLK)
    if (RST)
        rx_valid <= 1'b0;
    else if (i_rdy)
        rx_valid <= 1'b0;
    else if (RX_STB)
        rx_valid <= 1'b1;


reg x_stb;
reg x_error;

always @(posedge CLK)
    if (RST)
        x_stb <= 1'b0;
    else if(!x_stb && i_rdy)
        x_stb <= 1'b1;
    else if( x_stb)
        x_stb <= 1'b0;

always @(posedge CLK)
    if (i_rdy)
        x_error <= (rx_dat != tx_dat);

// ============================================================================
// Error counter and bitslip generator
reg [31:0] count_err;
reg        o_bitslip;

always @(posedge CLK)
    if (RST)
        count_err <= 0;
    else if (x_stb && x_error)
        count_err <= count_err + 1;
    else if (o_bitslip)
        count_err <= 0;

always @(posedge CLK)
    if (RST)
        o_bitslip <= 1'b0;
    else if (!o_bitslip && (count_err >= ERROR_COUNT))
        o_bitslip <= 1'b1;
    else if ( o_bitslip)
        o_bitslip <= 1'b0;

assign RX_BITSLIP = o_bitslip;

// ============================================================================
// Error output
reg [32:0]  o_cnt;

always @(posedge CLK)
    if (RST)
        o_cnt <= 0;
    else if (x_stb && x_error)
        o_cnt <= ERROR_HOLD;
    else
        o_cnt <= (o_cnt[32]) ? o_cnt : (o_cnt - 1);

assign O_ERROR = !o_cnt[32];

endmodule
