`default_nettype none

// ============================================================================

module receiver #
(
parameter WIDTH = 8,
parameter MODE  = "SDR"
)
(
input  wire CLK,
input  wire RST,

input  wire I_CLK,
input  wire I_DAT,

output wire             O_STB,
output wire [WIDTH-1:0] O_DAT,
input  wire             O_BITSLIP
);

// ============================================================================
// CLKDIV generation using a BUFR
wire i_clkdiv;
wire i_rstdiv;

// Divider for BUFR
localparam DIVIDE = (MODE == "SDR" && WIDTH == 2) ? "2" :
                    (MODE == "SDR" && WIDTH == 3) ? "3" :
                    (MODE == "SDR" && WIDTH == 4) ? "4" :
                    (MODE == "SDR" && WIDTH == 5) ? "5" :
                    (MODE == "SDR" && WIDTH == 6) ? "6" :
                    (MODE == "SDR" && WIDTH == 7) ? "7" :
                    (MODE == "SDR" && WIDTH == 8) ? "8" :

                    (MODE == "DDR" && WIDTH == 4) ? "2" :
                    (MODE == "DDR" && WIDTH == 6) ? "3" :
                    (MODE == "DDR" && WIDTH == 8) ? "4" : "BYPASS";
// BUFR
BUFR #
(
.BUFR_DIVIDE    (DIVIDE)
)
bufr_div
(
.I      (I_CLK),
.O      (i_clkdiv),
.CLR    (1'b0),
.CE     (1'b1)
);

// ISERDES reset generator
reg [3:0] rst_sr;
initial   rst_sr <= 4'hF;

always @(posedge i_clkdiv)
    if (RST) rst_sr <= 4'hF;
    else     rst_sr <= rst_sr >> 1;

assign i_rstdiv = rst_sr[0];

// ============================================================================
// ISERDES
wire [7:0] d_dat;

(* KEEP, DONT_TOUCH *)
ISERDESE2 #
(
.DATA_RATE          (MODE),
.DATA_WIDTH         (WIDTH),
.INTERFACE_TYPE     ("NETWORKING"),
.IS_CLKB_INVERTED   (1'b1)  // Do we have bits for that ??
)
iserdes
(
.CLK        (I_CLK),
.CLKB       (I_CLK),
.CLKDIV     (i_clkdiv),
.CE1        (1'b1),
.CE2        (1'b1),
.RST        (i_rstdiv),
.BITSLIP    (bitslip),

.D          (I_DAT),
.Q1         (d_dat[0]),
.Q2         (d_dat[1]),
.Q3         (d_dat[2]),
.Q4         (d_dat[3]),
.Q5         (d_dat[4]),
.Q6         (d_dat[5]),
.Q7         (d_dat[6]),
.Q8         (d_dat[7])
);

// ============================================================================
// Generate strobe synchronous to CLK
reg  clk_p;
reg  tick;

always @(posedge CLK)
    clk_p <= i_clkdiv;

always @(posedge CLK)
    if (RST)
        tick <= 1'b0;
    else
        tick <= !clk_p && i_clkdiv;

// ============================================================================
// Bitslip. The bitslip signal should be synchronous to the CLKDIV. Here it is
// asserted for as long as the CLKDIV period but it is not synchronous to it.
reg  bitslip_req;
reg  bitslip;

always @(posedge CLK)
    if (RST)
        bitslip_req <= 1'b0;
    else if (!bitslip_req && O_BITSLIP)
        bitslip_req <= 1'b1;
    else if (tick)
        bitslip_req <= 1'b0;

always @(posedge CLK)
    if (RST)
        bitslip <= 1'd0;
    else if (tick)
        bitslip <= bitslip_req;

// ============================================================================
// Output sync to CLK
reg              x_stb;
reg              o_stb;
reg  [WIDTH-1:0] o_dat;

always @(posedge CLK)
    if (RST)
        x_stb <= 1'b0;
    else if(!x_stb && tick)
        x_stb <= 1'b1;
    else if( x_stb)
        x_stb <= 1'b0;

always @(posedge CLK)
    if (RST)
        o_stb <= 1'd0;
    else
        o_stb <= x_stb;

always @(posedge CLK)
    if (x_stb)
        o_dat <= d_dat;

assign O_STB = o_stb;
assign O_DAT = o_dat[WIDTH-1:0];

endmodule
