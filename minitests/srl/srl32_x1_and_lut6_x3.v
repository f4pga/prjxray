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

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="A6LUT" *)
  SRLC32E srl_a
  (
  .CLK    (CLK),
  .CE     (CE),
  .D      (D),
  .A      (A),
  .Q      (Q[0])
  );

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="B6LUT" *)
  LUT6 lut_b
  (
  .I0     (I[0]),
  .I1     (I[1]),
  .I2     (I[2]),
  .I3     (I[3]),
  .I4     (I[4]),
  .I5     (I[5]),
  .O      (Q[1])
  );

  (* DONT_TOUCH="yes" *)
  (* LOC="SLICE_X2Y0", BEL="C6LUT" *)
  LUT6 lut_c
  (
  .I0     (I[0]),
  .I1     (I[1]),
  .I2     (I[2]),
  .I3     (I[3]),
  .I4     (I[4]),
  .I5     (I[5]),
  .O      (Q[2])
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
