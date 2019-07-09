module top
(
(* clock_buffer_type = "NONE" *)
input  wire CLK,
input  wire CE,
input  wire D,
input  wire [4:0] A,
output wire [2:0] Q
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

  (* LOC="SLICE_X2Y0", BEL="C6LUT"  *)
  SRLC32E srl_c
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q      (Q[2])
  );

endmodule
