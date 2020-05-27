// Copyright (C) 2017-2020  The Project X-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

`include "src/idelay_calibrator.v"

`default_nettype none

// ============================================================================

module top
(
input  wire clk,

input  wire rx,
output wire tx,

input  wire [15:0] sw,
output wire [15:0] led,

output wire ja1,
output wire ja2,
output wire ja3,
output wire ja4,
output wire ja7,
output wire ja8,
output wire ja9,
output wire ja10,

output wire jb1,
output wire jb2,
output wire jb3,
output wire jb4,
output wire jb7,
output wire jb8,
output wire jb9,
output wire jb10,

output wire jc1,
output wire jc2,
output wire jc3,
output wire jc4,
output wire jc7,
output wire jc8,
output wire jc9,
output wire jc10,

output wire xadc1_p,
output wire xadc2_p,
output wire xadc3_p,
output wire xadc4_p,
output wire xadc1_n,
output wire xadc2_n,
output wire xadc3_n,
output wire xadc4_n
);

// ============================================================================
// Clock & reset
reg [3:0] rst_sr;

initial rst_sr <= 4'hF;

always @(posedge clk)
    if (sw[0])
        rst_sr <= 4'hF;
    else
        rst_sr <= rst_sr >> 1;

wire CLK = clk;
wire RST = rst_sr[0];

// ============================================================================
// IDELAY calibrator
wire cal_rdy;

idelay_calibrator cal
(
.refclk (CLK),
.rst    (RST),
.rdy    (cal_rdy)
);

// ============================================================================

reg         dly_in;
wire [31:0] dly_out;

always @(posedge CLK)
    if (RST) dly_in <= 0;
    else     dly_in <= ~dly_in;

genvar i;
generate for (i=0; i<32; i=i+1) begin

    (* KEEP, DONT_TOUCH *)
    IDELAYE2 #
    (
    .IDELAY_TYPE    ("FIXED"),
    .IDELAY_VALUE   (i),
    .DELAY_SRC      ("DATAIN")
    )
    idelay
    (
    .DATAIN         (dly_in),
    .DATAOUT        (dly_out[i])
    );

end endgenerate

// ============================================================================
// I/O connections
reg [23:0] heartbeat_cnt;

always @(posedge CLK)
    heartbeat_cnt <= heartbeat_cnt + 1;

assign led[ 0] = heartbeat_cnt[23];
assign led[ 1] = cal_rdy;
assign led[ 2] = 1'b0;
assign led[ 3] = 1'b0;
assign led[ 4] = 1'b0;
assign led[ 5] = 1'b0;
assign led[ 6] = 1'b0;
assign led[ 7] = 1'b0;
assign led[ 8] = 1'b0;
assign led[ 9] = 1'b0;
assign led[10] = 1'b0;
assign led[11] = 1'b0;
assign led[12] = 1'b0;
assign led[13] = 1'b0;
assign led[14] = 1'b0;
assign led[15] = 1'b0;

assign ja1  = dly_out[ 0];
assign ja2  = dly_out[ 1];
assign ja3  = dly_out[ 2];
assign ja4  = dly_out[ 3];
assign ja7  = dly_out[ 4];
assign ja8  = dly_out[ 5];
assign ja9  = dly_out[ 6];
assign ja10 = dly_out[ 7];

assign jb1  = dly_out[ 8];
assign jb2  = dly_out[ 9];
assign jb3  = dly_out[10];
assign jb4  = dly_out[11];
assign jb7  = dly_out[12];
assign jb8  = dly_out[13];
assign jb9  = dly_out[14];
assign jb10 = dly_out[15];

assign jc1  = dly_out[16];
assign jc2  = dly_out[17];
assign jc3  = dly_out[18];
assign jc4  = dly_out[19];
assign jc7  = dly_out[20];
assign jc8  = dly_out[21];
assign jc9  = dly_out[22];
assign jc10 = dly_out[23];

assign xadc1_p = dly_out[24];
assign xadc2_p = dly_out[25];
assign xadc3_p = dly_out[26];
assign xadc4_p = dly_out[27];
assign xadc1_n = dly_out[28];
assign xadc2_n = dly_out[29];
assign xadc3_n = dly_out[30];
assign xadc4_n = dly_out[31];

endmodule
