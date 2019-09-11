`default_nettype none

// ============================================================================

module lfsr #
(
parameter WIDTH = 16, // LFSR width
parameter [WIDTH-1:0] POLY  = 16'hD008, // Polynomial
parameter [WIDTH-1:0] SEED  = 1 // Initial value
)
(
input  wire CLK,
input  wire CE,
input  wire RST,

output reg [WIDTH-1:0] O
);

wire feedback = ^(O & POLY);

always @(posedge CLK) begin
  if(RST) begin
    O <= SEED;
  end else if(CE) begin
    O <= {O[WIDTH-2:0], feedback};
  end
end

endmodule

