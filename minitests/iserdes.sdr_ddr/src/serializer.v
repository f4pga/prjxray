`default_nettype none

// ============================================================================

module serializer #
(
parameter WIDTH = 4,    // Serialization rate
parameter MODE  = "SDR" // "SDR" or "DDR"
)
(
// Clock & reset
input  wire CLK,
input  wire RST,

// Data input
input  wire[WIDTH-1:0] I,
output wire RD,
output wire CE,

// Serialized output
output wire O_CLK,
output wire O_DAT
);

// ============================================================================

generate if (MODE == "DDR" && (WIDTH & 1)) begin
    error for_DDR_mode_the_WIDTH_must_be_even ();
end endgenerate

// ============================================================================
// Output clock generation
reg  o_clk;
wire ce;

always @(posedge CLK)
    if (RST) o_clk <= 1'd1;
    else     o_clk <= !o_clk;

assign ce = !o_clk;

// ============================================================================
reg  [7:0]       count;
reg  [WIDTH-1:0] sreg;
wire             sreg_ld;

always @(posedge CLK)
    if (RST)            count <= 2;
    else if (ce) begin
        if (count == 0) count <= ((MODE == "DDR") ? (WIDTH/2) : WIDTH) - 1;
        else            count <= count - 1;
    end

assign sreg_ld = (count == 0);

always @(posedge CLK)
    if (ce) begin
        if (sreg_ld) sreg <= I;
        else         sreg <= sreg << ((MODE == "DDR") ? 2 : 1);
    end

wire [1:0] o_dat = sreg[WIDTH-1:WIDTH-2];

// ============================================================================
// SDR/DDR output FFs
reg o_reg;

always @(posedge CLK)
    if      (!o_clk && MODE == "SDR") o_reg <= o_dat[1]; // +
    else if (!o_clk && MODE == "DDR") o_reg <= o_dat[0]; // +
    else if ( o_clk && MODE == "DDR") o_reg <= o_dat[1]; // -
    else                              o_reg <= o_reg;

// ============================================================================

assign O_DAT = o_reg;
assign O_CLK = o_clk;

assign RD = (count == 1);
assign CE = ce;

endmodule
