`default_nettype none

module plle2_test
(
input  wire         CLK,
input  wire         RST,

input  wire         I_CLKINSEL,
output wire         O_LOCKED,
output wire [5:0]   O_CNT
);

// ============================================================================
// Input clock divider (to get different clkins)
wire clk100;
reg  clk50;

assign clk100 = CLK;

always @(posedge clk100)
    clk50 <= !clk50;

// ============================================================================
// The PLL
wire clk_fb_o;
wire clk_fb_i;

wire [5:0] clk;

PLLE2_ADV #
(
.BANDWIDTH          ("HIGH"),
.COMPENSATION       ("BUF_IN"),

.CLKIN1_PERIOD      (20.0),  // 50MHz
.CLKIN2_PERIOD      (10.0),  // 100MHz

.CLKFBOUT_MULT      (16),
.CLKFBOUT_PHASE     (0.0),

.CLKOUT0_DIVIDE     (16),
.CLKOUT0_DUTY_CYCLE (0.53125),
.CLKOUT0_PHASE      (45.0),

.CLKOUT1_DIVIDE     (32),
.CLKOUT1_DUTY_CYCLE (0.5),
.CLKOUT1_PHASE      (90.0),

.CLKOUT2_DIVIDE     (48),
.CLKOUT2_DUTY_CYCLE (0.5),
.CLKOUT2_PHASE      (135.0),

.CLKOUT3_DIVIDE     (64),
.CLKOUT3_DUTY_CYCLE (0.5),
.CLKOUT3_PHASE      (-45.0),

.CLKOUT4_DIVIDE     (80),
.CLKOUT4_DUTY_CYCLE (0.5),
.CLKOUT4_PHASE      (-90.0),

.CLKOUT5_DIVIDE     (96),
.CLKOUT5_DUTY_CYCLE (0.5),
.CLKOUT5_PHASE      (-135.0),

.STARTUP_WAIT       ("FALSE")
)
pll
(
.CLKIN1     (clk50),
.CLKIN2     (clk100),
.CLKINSEL   (I_CLKINSEL),

.RST        (RST),
.LOCKED     (O_LOCKED),

.CLKFBIN    (clk_fb_i),
.CLKFBOUT   (clk_fb_o),

.CLKOUT0    (clk[0]),
.CLKOUT1    (clk[1]),
.CLKOUT2    (clk[2]),
.CLKOUT3    (clk[3]),
.CLKOUT4    (clk[4]),
.CLKOUT5    (clk[5])
);

BUFG clk_fb_buf (.I(clk_fb_o), .O(clk_fb_i));

// ============================================================================
// Counters

wire rst = RST || !O_LOCKED;

genvar i;
generate for (i=0; i<6; i=i+1) begin

  reg [23:0] counter;

  always @(posedge clk[i] or posedge rst)
      if (rst) counter <= 0;
      else     counter <= counter + 1;

  assign O_CNT[i] = counter[21];

end endgenerate

endmodule
