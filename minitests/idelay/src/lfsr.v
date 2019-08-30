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
