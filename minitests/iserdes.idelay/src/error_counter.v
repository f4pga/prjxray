`default_nettype none

// ============================================================================

module error_counter #
(
parameter COUNT_WIDTH = 24,
parameter DELAY_TAPS  = 32,

parameter TRIGGER_INTERVAL = 20,//100000000,
parameter HOLDOFF_TIME     = 4,//10,
parameter MEASURE_TIME     = 10//50000
)
(
input  wire CLK,
input  wire RST,

input  wire I_STB,
input  wire I_ERR,

output wire DLY_LD,
output wire [$clog2(DELAY_TAPS)-1:0] DLY_CNT,

output wire O_STB,
output wire [COUNT_WIDTH*DELAY_TAPS-1:0] O_DAT
);

// ============================================================================
// FSM
integer fsm;

localparam FSM_IDLE     = 'h00;
localparam FSM_SETUP    = 'h10;
localparam FSM_HOLDOFF  = 'h20;
localparam FSM_PREPARE  = 'h30;
localparam FSM_MEASURE  = 'h40;
localparam FSM_STORE    = 'h50;
localparam FSM_OUTPUT   = 'h60;

// ============================================================================
// Counters
reg [32:0] ps_cnt;
reg [$clog2(DELAY_TAPS)-1:0] dly_cnt;

initial ps_cnt <= TRIGGER_INTERVAL - 1;

always @(posedge CLK)
    case (fsm)

    FSM_IDLE:       ps_cnt <= ps_cnt - 1;
    FSM_SETUP:      ps_cnt <= HOLDOFF_TIME - 1;
    FSM_HOLDOFF:    ps_cnt <= ps_cnt - 1;
    FSM_PREPARE:    ps_cnt <= MEASURE_TIME - 1;
    FSM_MEASURE:    ps_cnt <= ps_cnt - 1;
    FSM_OUTPUT:     ps_cnt <= TRIGGER_INTERVAL - 1;

    endcase

always @(posedge CLK)
    case (fsm)

    FSM_IDLE:       dly_cnt <= 0;
    FSM_STORE:      dly_cnt <= dly_cnt + 1;

    endcase

// ============================================================================
// IDELAY control
assign DLY_LD  = (fsm == FSM_SETUP);
assign DLY_CNT = dly_cnt;

// ============================================================================
// Error counter and output shift register
reg [(COUNT_WIDTH*DELAY_TAPS)-1:0] o_dat_sr;
reg [COUNT_WIDTH-1:0] err_cnt;

always @(posedge CLK)
    case (fsm)

    FSM_PREPARE:           err_cnt <= 0;
    FSM_MEASURE: if(I_STB) err_cnt <= err_cnt + I_ERR;

    endcase

always @(posedge CLK)
    if (fsm == FSM_STORE)
        o_dat_sr <= (o_dat_sr << COUNT_WIDTH) | err_cnt;

// ============================================================================
// Control FSM
always @(posedge CLK)
    if (RST)
        fsm <= FSM_IDLE;
    else case (fsm)

    FSM_IDLE:       if (ps_cnt == 0)  fsm <= FSM_SETUP;
    FSM_SETUP:      fsm <= FSM_HOLDOFF;
    FSM_HOLDOFF:    if (ps_cnt == 0)  fsm <= FSM_PREPARE;
    FSM_PREPARE:    fsm <= FSM_MEASURE;
    FSM_MEASURE:    if (ps_cnt == 0)  fsm <= FSM_STORE;
    FSM_STORE:      if (dly_cnt == (DELAY_TAPS-1))
                        fsm <= FSM_OUTPUT;
                    else
                        fsm <= FSM_SETUP;
    FSM_OUTPUT:     fsm <= FSM_IDLE;

    endcase

// ============================================================================
// Output
assign O_STB = (fsm == FSM_OUTPUT);
assign O_DAT = o_dat_sr;

endmodule

