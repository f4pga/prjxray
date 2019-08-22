`default_nettype none

// ============================================================================

module trx_path #
(
parameter WIDTH = 8,
parameter MODE  = "SDR"
)
(
// Clock and reset
input  wire CLK,
input  wire RST,

// Input and output pins
output wire O_CLK,
output wire O_DAT,
input  wire I_DAT,

// Error indicator
output wire ERROR
);

// ============================================================================

wire tx_stb;
wire [WIDTH-1:0] tx_dat;

wire rx_stb;
wire [WIDTH-1:0] rx_dat;
wire rx_bitslip;

wire s_clk;

// Transmitter
transmitter #
(
.WIDTH  (WIDTH),
.MODE   (MODE)
)
transmitter
(
.CLK        (CLK),
.RST        (RST),

.O_STB      (tx_stb),
.O_DAT      (tx_dat),

.S_CLK      (s_clk),
.S_DAT      (O_DAT)
);

assign O_CLK = s_clk;

// Receiver
receiver #
(
.WIDTH  (WIDTH),
.MODE   (MODE)
)
receiver
(
.CLK        (CLK),
.RST        (RST),

.I_CLK      (s_clk),
.I_DAT      (I_DAT),

.O_STB      (rx_stb),
.O_DAT      (rx_dat),
.O_BITSLIP  (rx_bitslip)
);

// The comparator module generates bitslip signal for the receiver. However
// the bitslip can shift only modulo WIDTH. Therefore additional delay is
// added which can delay the transmitted data that we compare to by a number
// of full words.

// Count bitslip pulses to know how much to delay words
reg [3:0] rx_bitslip_cnt;
always @(posedge CLK)
    if (RST)
        rx_bitslip_cnt <= 0;
    else if (rx_bitslip) begin
        if (rx_bitslip_cnt == (2*WIDTH - 1))
            rx_bitslip_cnt <= 0;
        else
            rx_bitslip_cnt <= rx_bitslip_cnt + 1;
    end

// Word delay
reg  [1:0]       tx_dly_cnt;
reg  [WIDTH-1:0] tx_dat_dly_a;
reg  [WIDTH-1:0] tx_dat_dly_b;
reg  [WIDTH-1:0] tx_dat_dly_c;
reg  [WIDTH-1:0] tx_dat_dly_d;
wire [WIDTH-1:0] tx_dat_dly;

always @(posedge CLK)
    if (RST)
        tx_dly_cnt <= 0;
    else if(rx_bitslip && rx_bitslip_cnt == (2*WIDTH - 1))
        tx_dly_cnt <= tx_dly_cnt + 1;

always @(posedge CLK)
    if (tx_stb) begin
        tx_dat_dly_d <= tx_dat_dly_c;
        tx_dat_dly_c <= tx_dat_dly_b;
        tx_dat_dly_b <= tx_dat_dly_a;
        tx_dat_dly_a <= tx_dat;
    end

assign tx_dat_dly = (tx_dly_cnt == 0) ?  tx_dat_dly_a :
                    (tx_dly_cnt == 1) ?  tx_dat_dly_b :
                    (tx_dly_cnt == 2) ?  tx_dat_dly_c :
                  /*(tx_dly_cnt == 3) ?*/tx_dat_dly_d;

// Comparator
comparator #
(
.WIDTH  (WIDTH)
)
comparator
(
.CLK        (CLK),
.RST        (RST),

.TX_STB     (tx_stb),
.TX_DAT     (tx_dat_dly),

.RX_STB     (rx_stb),
.RX_DAT     (rx_dat),
.RX_BITSLIP (rx_bitslip),

.O_ERROR    (ERROR)
);

endmodule
