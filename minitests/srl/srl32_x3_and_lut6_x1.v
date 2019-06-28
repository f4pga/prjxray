module top
(
(* clock_buffer_type = "NONE" *)
input  wire CLK,
input  wire CE,
input  wire D,
input  wire [5:0] I,
input  wire [4:0] A,
output wire [3:0] Q
);

  wire srl_b_mc31;
  wire srl_c_mc31;

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="A6LUT" *)
  SRLC32E srl_a
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (srl_b_mc31),
  .A      (A),
  .Q      (Q[0])
  );

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="B6LUT" *)
  SRLC32E srl_b
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (srl_c_mc31),
  .A      (A),
  .Q      (Q[1]),
  .Q31    (srl_b_mc31)
  );

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="C6LUT" *)
  SRLC32E srl_c
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q      (Q[2]),
  .Q31    (srl_c_mc31)
  );

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="D6LUT" *)
  LUT6 lut_d
  (
  .I0     (I[0]),
  .I1     (I[1]),
  .I2     (I[2]),
  .I3     (I[3]),
  .I4     (I[4]),
  .I5     (I[5]),
  .O      (Q[3])
  );

endmodule
