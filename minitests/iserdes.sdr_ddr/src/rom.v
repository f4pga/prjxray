
`default_nettype none

// ============================================================================

module rom
(
input  wire CLK,
input  wire RST,

input  wire RD,
output wire [7:0] O
);

// ============================================================================

reg [7:0] rom[0:31];

initial begin
  rom[   0] <= 8'd157;
  rom[   1] <= 8'd254;
  rom[   2] <= 8'd208;
  rom[   3] <= 8'd125;
  rom[   4] <= 8'd39;
  rom[   5] <= 8'd192;
  rom[   6] <= 8'd242;
  rom[   7] <= 8'd117;
  rom[   8] <= 8'd186;
  rom[   9] <= 8'd94;
  rom[  10] <= 8'd201;
  rom[  11] <= 8'd156;
  rom[  12] <= 8'd224;
  rom[  13] <= 8'd120;
  rom[  14] <= 8'd255;
  rom[  15] <= 8'd219;
  rom[  16] <= 8'd12;
  rom[  17] <= 8'd53;
  rom[  18] <= 8'd156;
  rom[  19] <= 8'd93;
  rom[  20] <= 8'd97;
  rom[  21] <= 8'd47;
  rom[  22] <= 8'd9;
  rom[  23] <= 8'd184;
  rom[  24] <= 8'd68;
  rom[  25] <= 8'd235;
  rom[  26] <= 8'd67;
  rom[  27] <= 8'd68;
  rom[  28] <= 8'd216;
  rom[  29] <= 8'd26;
  rom[  30] <= 8'd16;
  rom[  31] <= 8'd93;
end

reg [7:0] dat;
reg [4:0] adr;

always @(posedge CLK)
  if (RST)     adr <= 0;
  else if (RD) adr <= adr + 1;

always @(posedge CLK)
  if (RD) dat <= rom[adr];

assign O = dat;

// ============================================================================

endmodule

