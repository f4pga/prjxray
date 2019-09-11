// This module compares two bitstreams and automatically determines their
// offset. This is done by iteratively changing bit delay for I_DAT_REF
// every time the number of errors exceeds ERROR_COUNT. The output O_ERROR
// signal is high for at least ERROR_HOLD cycles.

`default_nettype none

// ============================================================================

module comparator #
(
parameter ERROR_COUNT = 8,
parameter ERROR_HOLD  = 2500000
)
(
input  wire CLK,
input  wire RST,

input  wire I_DAT_REF,
input  wire I_DAT_IOB,

output wire O_ERROR
);

// ============================================================================
// Data latch
reg [2:0] i_dat_ref_sr;
reg [2:0] i_dat_iob_sr;

always @(posedge CLK)
    i_dat_ref_sr <= (i_dat_ref_sr << 1) | I_DAT_REF;
always @(posedge CLK)
    i_dat_iob_sr <= (i_dat_iob_sr << 1) | I_DAT_IOB;

wire i_dat_ref = i_dat_ref_sr[2];
wire i_dat_iob = i_dat_iob_sr[2];

// ============================================================================
// Shift register for reference data, shift strobe generator.
reg  [31:0] sreg;
reg  [ 4:0] sreg_sel;
wire        sreg_dat;
reg         sreg_sh;

always @(posedge CLK)
    sreg <= (sreg << 1) | i_dat_ref;

always @(posedge CLK)
    if (RST)
        sreg_sel <= 0;
    else if(sreg_sh)
        sreg_sel <= sreg_sel + 1;

assign sreg_dat = sreg[sreg_sel];

// ============================================================================
// Comparator and error counter
wire        cmp_err;
reg  [31:0] err_cnt;

assign cmp_err = sreg_dat ^ i_dat_iob;

always @(posedge CLK)
    if (RST)
        err_cnt <= 0;
    else if(sreg_sh)
        err_cnt <= 0;
    else if(cmp_err)
        err_cnt <= err_cnt + 1;

always @(posedge CLK)
    if (RST)
        sreg_sh <= 0;
    else if(~sreg_sh && (err_cnt == ERROR_COUNT))
        sreg_sh <= 1;
    else
        sreg_sh <= 0;

// ============================================================================
// Output generator
reg [24:0] o_cnt;

always @(posedge CLK)
    if (RST)
        o_cnt <= -1;
    else if (cmp_err)
        o_cnt <= ERROR_HOLD - 2;
    else if (~o_cnt[24])
        o_cnt <= o_cnt - 1;

assign O_ERROR = !o_cnt[24];

endmodule
