module top
(
(* clock_buffer_type = "NONE" *)
input  wire CLK,
input  wire CE,
input  wire D,
input  wire [4:0] A,
output wire Q
);

  wire  q31_d;
  wire  q31_c;
  wire  q31_b;

  (* LOC="SLICE_X2Y0", BEL="D6LUT"  *)
  SRLC32E srl_d
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q31    (q31_d)
  );

  (* LOC="SLICE_X2Y0", BEL="C6LUT"  *)
  SRLC32E srl_c
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (q31_d),
  .A      (A),
  .Q31    (q31_c)
  );

  (* LOC="SLICE_X2Y0", BEL="B6LUT"  *)
  SRLC32E srl_b
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (q31_c),
  .A      (A),
  .Q      (q31_b)
  );

  (* LOC="SLICE_X2Y0", BEL="A6LUT"  *)
  SRLC32E srl_a
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (q31_b),
  .A      (A),
  .Q      (Q)
  );

endmodule
