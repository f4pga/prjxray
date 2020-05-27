// Copyright (C) 2017-2020  The Project X-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

`default_nettype none

// ============================================================================

module lfsr #
(
  parameter WIDTH = 16,
  parameter [WIDTH-1:0] POLY  = 16'hD008,
  parameter [WIDTH-1:0] SEED  = 1
)
(
  input  wire clk,
  input  wire rst,
  input  wire ce,
  output reg [WIDTH-1:0] r
);

  wire feedback = ^(r & POLY);

  always @(posedge clk) begin
    if(rst) begin
      r <= SEED;
    end else if(ce) begin
      r <= {r[WIDTH-2:0], feedback};
    end
  end

endmodule
