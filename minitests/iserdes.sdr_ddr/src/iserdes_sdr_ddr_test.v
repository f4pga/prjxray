`default_nettype none

// ============================================================================

module iserdes_sdr_ddr_test #
(
parameter DATA_WIDTH = 8,
parameter DATA_RATE  = "SDR"
)
(
// Clock and reset
input  wire CLK,
input  wire RST,

// Data pin
inout  wire IO_DAT,

// Error indicator
output wire O_ERROR
);

// ============================================================================
// IOB
wire iob_o;
wire iob_i;

OBUFT obuf
(
.I      (iob_o),
.T      (1'b0),
.O      (IO_DAT)
);

IBUF ibuf
(
.I      (IO_DAT),
.O      (iob_i)
);

// ============================================================================

wire tx_stb;
wire [DATA_WIDTH-1:0] tx_dat;

wire rx_stb;
wire [DATA_WIDTH-1:0] rx_dat;
wire rx_bitslip;

wire s_clk;

// Transmitter
transmitter #
(
.WIDTH  (DATA_WIDTH),
.MODE   (DATA_RATE)
)
transmitter
(
.CLK        (CLK),
.RST        (RST),

.O_STB      (tx_stb),
.O_DAT      (tx_dat),

.S_CLK      (s_clk),
.S_DAT      (iob_o)
);

// Receiver
receiver #
(
.WIDTH  (DATA_WIDTH),
.MODE   (DATA_RATE)
)
receiver
(
.CLK        (CLK),
.RST        (RST),

.I_CLK      (s_clk),
.I_DAT      (iob_i),

.O_STB      (rx_stb),
.O_DAT      (rx_dat),
.O_BITSLIP  (rx_bitslip)
);

// The comparator module generates bitslip signal for the receiver. However
// the bitslip can shift only modulo DATA_WIDTH. Therefore additional delay is
// added which can delay the transmitted data that we compare to by a number
// of full words.

// Count bitslip pulses to know how much to delay words
reg [3:0] rx_bitslip_cnt;
always @(posedge CLK)
    if (RST)
        rx_bitslip_cnt <= 0;
    else if (rx_bitslip) begin
        if (rx_bitslip_cnt == (2*DATA_WIDTH - 1))
            rx_bitslip_cnt <= 0;
        else
            rx_bitslip_cnt <= rx_bitslip_cnt + 1;
    end

// Word delay
reg  [1:0] tx_dly_cnt;
reg  [DATA_WIDTH-1:0] tx_dat_dly_a;
reg  [DATA_WIDTH-1:0] tx_dat_dly_b;
reg  [DATA_WIDTH-1:0] tx_dat_dly_c;
reg  [DATA_WIDTH-1:0] tx_dat_dly_d;
wire [DATA_WIDTH-1:0] tx_dat_dly;

always @(posedge CLK)
    if (RST)
        tx_dly_cnt <= 0;
    else if(rx_bitslip && rx_bitslip_cnt == (2*DATA_WIDTH - 1))
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
.WIDTH  (DATA_WIDTH)
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

.O_ERROR    (O_ERROR)
);

endmodule
