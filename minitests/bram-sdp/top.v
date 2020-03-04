module top (
);

  // Both RAMB18 in the same tile
  (* KEEP, DONT_TOUCH, LOC="RAMB18_X0Y25" *)
  RAMB18E1 #(
    .RAM_MODE("SDP"),
    .READ_WIDTH_A(36),
    .READ_WIDTH_B(0),
    .WRITE_MODE_A("READ_FIRST"),
    .WRITE_MODE_B("READ_FIRST"),
    .WRITE_WIDTH_A(0),
    .WRITE_WIDTH_B(36)
  ) RAMB18E1_BOTH_X1  (
    .ENARDEN(1'b1),
    .ENBWREN(1'b1),
    .REGCEAREGCE(1'b1),
    .REGCEB(1'b0),
    .RSTRAMARSTRAM(1'b1),
    .RSTRAMB(1'b1),
    .RSTREGARSTREG(1'b1),
    .RSTREGB(1'b1),
    .WEA({1'b0}),
    .WEBWE({1'b0})
  );

  (* KEEP, DONT_TOUCH, LOC="RAMB18_X0Y24" *)
  RAMB18E1 #(
    .RAM_MODE("SDP"),
    .READ_WIDTH_A(36),
    .READ_WIDTH_B(0),
    .WRITE_MODE_A("READ_FIRST"),
    .WRITE_MODE_B("READ_FIRST"),
    .WRITE_WIDTH_A(0),
    .WRITE_WIDTH_B(36)
  ) RAMB18E1_BOTH_X0  (
    .ENARDEN(1'b1),
    .ENBWREN(1'b1),
    .REGCEAREGCE(1'b1),
    .REGCEB(1'b0),
    .RSTRAMARSTRAM(1'b1),
    .RSTRAMB(1'b1),
    .RSTREGARSTREG(1'b1),
    .RSTREGB(1'b1),
    .WEA({1'b0}),
    .WEBWE({1'b0})
  );

  // ---------------------------------------

  // One RAMB18 in Y0
  (* KEEP, DONT_TOUCH, LOC="RAMB18_X0Y22" *)
  RAMB18E1 #(
    .RAM_MODE("SDP"),
    .READ_WIDTH_A(36),
    .READ_WIDTH_B(0),
    .WRITE_MODE_A("READ_FIRST"),
    .WRITE_MODE_B("READ_FIRST"),
    .WRITE_WIDTH_A(0),
    .WRITE_WIDTH_B(36)
  ) RAMB18E1_X0  (
    .ENARDEN(1'b1),
    .ENBWREN(1'b1),
    .REGCEAREGCE(1'b1),
    .REGCEB(1'b0),
    .RSTRAMARSTRAM(1'b1),
    .RSTRAMB(1'b1),
    .RSTREGARSTREG(1'b1),
    .RSTREGB(1'b1),
    .WEA({1'b0}),
    .WEBWE({1'b0})
  );

  // ---------------------------------------

  // One RAMB18 in Y1
  (* KEEP, DONT_TOUCH, LOC="RAMB18_X0Y21" *)
  RAMB18E1 #(
    .RAM_MODE("SDP"),
    .READ_WIDTH_A(36),
    .READ_WIDTH_B(0),
    .WRITE_MODE_A("READ_FIRST"),
    .WRITE_MODE_B("READ_FIRST"),
    .WRITE_WIDTH_A(0),
    .WRITE_WIDTH_B(36)
  ) RAMB18E1_X1  (
    .ENARDEN(1'b1),
    .ENBWREN(1'b1),
    .REGCEAREGCE(1'b1),
    .REGCEB(1'b0),
    .RSTRAMARSTRAM(1'b1),
    .RSTRAMB(1'b1),
    .RSTREGARSTREG(1'b1),
    .RSTREGB(1'b1),
    .WEA({1'b0}),
    .WEBWE({1'b0})
  );


  // ---------------------------------------

  // One RAMB36
  (* KEEP, DONT_TOUCH, LOC="RAMB36_X0Y9" *)
  RAMB36E1 #(
    .RAM_MODE("SDP"),
    .READ_WIDTH_A(72),
    .READ_WIDTH_B(0),
    .WRITE_MODE_A("READ_FIRST"),
    .WRITE_MODE_B("READ_FIRST"),
    .WRITE_WIDTH_A(0),
    .WRITE_WIDTH_B(72)
  ) RAMB36E1_X0  (
    .ENARDEN(1'b1),
    .ENBWREN(1'b1),
    .REGCEAREGCE(1'b1),
    .REGCEB(1'b0),
    .RSTRAMARSTRAM(1'b1),
    .RSTRAMB(1'b1),
    .RSTREGARSTREG(1'b1),
    .RSTREGB(1'b1),
    .WEA({1'b0}),
    .WEBWE({1'b0})
  );


endmodule
