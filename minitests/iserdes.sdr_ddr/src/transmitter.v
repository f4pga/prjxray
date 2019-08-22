`default_nettype none

// ============================================================================

module transmitter #
(
parameter WIDTH = 8,
parameter MODE  = "SDR"
)
(
// Input clock and reset
input  wire CLK,
input  wire RST,

// Data for comparison
output wire O_STB,
output wire [WIDTH-1:0] O_DAT,

// Serialized clock and data
output wire S_CLK,
output wire S_CE,
output wire S_DAT
);

// ============================================================================
// ROM
wire s_clk;
wire s_ce;
wire s_dat;

wire [WIDTH-1:0] rom_dat;
wire rom_rd;

rom rom
(
.CLK    (CLK),
.RST    (RST),

.RD     (rom_rd & s_ce),
.O      (rom_dat)  // Truncate bits if WIDTH < 8 here.
);

// ============================================================================
// Serializer

serializer #
(
.WIDTH  (WIDTH),
.MODE   (MODE)
)
serializer
(
.CLK    (CLK),
.RST    (RST),

.I      (rom_dat),
.RD     (rom_rd),
.CE     (s_ce),

.O_CLK  (s_clk),
.O_DAT  (s_dat)
);

assign S_CLK = s_clk;
assign S_CE  = s_ce;
assign S_DAT = s_dat;

// ============================================================================
// Parallel output (for later comparison)
reg             o_stb;

always @(posedge CLK)
    if (RST) o_stb <= 1'b0;
    else if (!o_stb && s_ce && rom_rd) o_stb <= 1'b1;
    else if ( o_stb) o_stb <= 1'd0;

assign O_STB = o_stb;
assign O_DAT = rom_dat;

// ============================================================================

endmodule
