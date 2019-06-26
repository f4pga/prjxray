module top
(
(* clock_buffer_type = "NONE" *)
input  wire CLK,
input  wire CE,
input  wire D,
input  wire [4:0] A,
output wire [1:0] Q
);

  (* LOC="SLICE_X2Y0", BEL="A6LUT"  *)
  SRLC32E srl_a
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q      (Q[0])
  );

  (* LOC="SLICE_X2Y0", BEL="B6LUT"  *)
  SRLC32E srl_b
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q      (Q[1])
  );

endmodule
