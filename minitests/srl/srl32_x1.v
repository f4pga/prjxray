module top
(
(* clock_buffer_type = "NONE" *)
input  wire CLK,
input  wire CE,
input  wire D,
input  wire [4:0] A,
output wire Q
);

  (* LOC="SLICE_X2Y0", BEL="A6LUT"  *)
  SRLC32E srl_a
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q      (Q)
  );

endmodule
