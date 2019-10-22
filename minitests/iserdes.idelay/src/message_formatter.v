`default_nettype none

// ============================================================================

module message_formatter #
(
parameter WIDTH = 24,       // Word length in bits. MUST be a multiply of 4
parameter COUNT = 2,        // Word count
parameter TX_INTERVAL = 4   // Character transmission interval
)
(
// Clock and reset
input  wire CLK,
input  wire RST,

// Data input
input  wire I_STB,
input  wire [(WIDTH*COUNT)-1:0] I_DAT,

// ASCII output
output wire O_STB,
output wire [7:0] O_DAT
);

// ============================================================================

// Total input data word width
localparam TOTAL_WIDTH = WIDTH * COUNT;

// ============================================================================
// FSM states
integer fsm;

localparam FSM_IDLE     = 'h00;
localparam FSM_TX_HEX   = 'h11;
localparam FSM_TX_CR    = 'h21;
localparam FSM_TX_LF    = 'h22;
localparam FSM_TX_SEP   = 'h31;

// ============================================================================
// TX interval counter
reg [24:0]  tx_dly_cnt;
reg         tx_req;
wire        tx_rdy;

always @(posedge CLK)
    if (RST)
        tx_dly_cnt <= -1;
    else if (!tx_rdy)
        tx_dly_cnt <= tx_dly_cnt  - 1;
    else if ( tx_rdy && tx_req)
        tx_dly_cnt <= TX_INTERVAL - 2;

assign tx_rdy = tx_dly_cnt[24];

always @(posedge CLK)
    if (RST)
        tx_req <= 1'b0;
    else case (fsm)

    FSM_TX_HEX: tx_req <= 1'b1;
    FSM_TX_SEP: tx_req <= 1'b1;
    FSM_TX_CR:  tx_req <= 1'b1;
    FSM_TX_LF:  tx_req <= 1'b1;

    default:    tx_req <= 1'b0;

    endcase

// ============================================================================
// Word and char counter
reg  [7:0] char_cnt;
reg  [7:0] word_cnt;

always @(posedge CLK)
    if (fsm == FSM_IDLE || fsm == FSM_TX_SEP)
        char_cnt <= (WIDTH/4) - 1;
    else if (tx_rdy && fsm == FSM_TX_HEX)
        char_cnt <= char_cnt - 1;

always @(posedge CLK)
    if (fsm == FSM_IDLE)
        word_cnt <= COUNT - 1;
    else if (tx_rdy && fsm == FSM_TX_SEP)
        word_cnt <= word_cnt - 1;

// ============================================================================
// Data shift register
reg  [TOTAL_WIDTH-1:0] sr_reg;
wire [3:0] sr_dat;

always @(posedge CLK)
    if (fsm == FSM_IDLE && I_STB)
        sr_reg <= I_DAT;
    else if (fsm == FSM_TX_HEX && tx_rdy)
        sr_reg <= sr_reg << 4;

assign sr_dat = sr_reg[TOTAL_WIDTH-1:TOTAL_WIDTH-4];

// ============================================================================
// Control FSM
always @(posedge CLK)
    if (RST)
        fsm <= FSM_IDLE;
    else case (fsm)

    FSM_IDLE:   if (I_STB) fsm <= FSM_TX_HEX;

    FSM_TX_HEX:
                if (tx_rdy && (char_cnt == 0) && (word_cnt == 0))
                    fsm <= FSM_TX_CR;
                else if (tx_rdy && (char_cnt == 0)) fsm <= FSM_TX_SEP;
                else if (tx_rdy && (char_cnt != 0)) fsm <= FSM_TX_HEX;

    FSM_TX_SEP: if (tx_rdy) fsm <= FSM_TX_HEX;
    FSM_TX_CR:  if (tx_rdy) fsm <= FSM_TX_LF;
    FSM_TX_LF:  if (tx_rdy) fsm <= FSM_IDLE;

    endcase

// ============================================================================
// Data to ASCII converter
reg        o_stb;
reg  [7:0] o_dat;

always @(posedge CLK or posedge RST)
    if (RST)
        o_stb <= 1'd0;
    else
        o_stb <= tx_req & tx_rdy;

always @(posedge CLK)
    if      (fsm == FSM_TX_CR)
        o_dat <= 8'h0D;
    else if (fsm == FSM_TX_LF)
        o_dat <= 8'h0A;
    else if (fsm == FSM_TX_SEP)
        o_dat <= "_";
    else if (fsm == FSM_TX_HEX) case (sr_dat)
        4'h0: o_dat <= "0";
        4'h1: o_dat <= "1";
        4'h2: o_dat <= "2";
        4'h3: o_dat <= "3";
        4'h4: o_dat <= "4";
        4'h5: o_dat <= "5";
        4'h6: o_dat <= "6";
        4'h7: o_dat <= "7";
        4'h8: o_dat <= "8";
        4'h9: o_dat <= "9";
        4'hA: o_dat <= "A";
        4'hB: o_dat <= "B";
        4'hC: o_dat <= "C";
        4'hD: o_dat <= "D";
        4'hE: o_dat <= "E";
        4'hF: o_dat <= "F";
    endcase

assign O_STB = o_stb;
assign O_DAT = o_dat;

endmodule
