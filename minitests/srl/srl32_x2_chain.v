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
  .Q      (Q)
  );

endmodule
