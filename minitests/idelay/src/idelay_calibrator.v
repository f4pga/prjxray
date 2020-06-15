// Copyright (C) 2017-2020  The Project X-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

`default_nettype none

// ============================================================================

module idelay_calibrator #
(
parameter SITE_LOC = ""
)
(
input  wire refclk,  // REFCLK for IDELAYCTRL
input  wire rst,     // External reset

output wire rdy      // Output ready signal
);

// ============================================================================
// Long reset generator (~60ns for Artix 7 according to the datasheet)

reg  [6:0] r_cnt;
wire       r_rst;

initial r_cnt <= 0;

always @(posedge refclk)
    if (rst)
        r_cnt <= 0;
    else if (r_rst)
        r_cnt <= r_cnt + 1;

assign r_rst = !r_cnt[6];

// ============================================================================
// IDELAYCTRL

(* KEEP, DONT_TOUCH, LOC = SITE_LOC *)
IDELAYCTRL idelayctlr
(
.REFCLK (refclk),
.RST    (r_rst),
.RDY    (rdy)
);

endmodule
