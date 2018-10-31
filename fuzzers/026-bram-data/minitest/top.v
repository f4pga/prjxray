`ifndef ROI
ERROR: must set ROI
`endif

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 256;
	localparam integer DOUT_N = 256;

	reg [DIN_N-1:0] din;
	wire [DOUT_N-1:0] dout;

	reg [DIN_N-1:0] din_shr;
	reg [DOUT_N-1:0] dout_shr;

	always @(posedge clk) begin
		din_shr <= {din_shr, di};
		dout_shr <= {dout_shr, din_shr[DIN_N-1]};
		if (stb) begin
			din <= din_shr;
			dout_shr <= dout;
		end
	end

	assign do = dout_shr[DOUT_N-1];

    `ROI
	    roi (
		.clk(clk),
		.din(din),
		.dout(dout)
	);
endmodule

/******************************************************************************
*******************************************************************************
DATA ROI
*******************************************************************************
******************************************************************************/

/******************************************************************************
Toggle a single data bit to locate a single instance (BRAM36)
******************************************************************************/

module roi_bram36d_bit0(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

module roi_bram36d_bit1(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

/******************************************************************************
Toggle a single data bit to locate a single instance (BRAM18)
******************************************************************************/

module roi_bram18d_bit0(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB18E1 #(.LOC("RAMB18_X0Y20"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

module roi_bram18d_bit1(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB18E1 #(.LOC("RAMB18_X0Y20"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

/******************************************************************************
Toggle all bits to show the size of the data section
******************************************************************************/

module roi_bramd_bits0(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0({256{1'b0}}), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

module roi_bramd_bits1(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0({256{1'b1}}), .INIT({256{1'b1}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

/******************************************************************************
Toggle one bit per BRAM in the ROI to show pitch between entries
******************************************************************************/

module roi_bramds_bit0(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y21"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y22"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y23"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y24"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r4(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y25"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r5(.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y26"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r6(.clk(clk), .din(din[  48 +: 8]), .dout(dout[  48 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y27"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r7(.clk(clk), .din(din[  56 +: 8]), .dout(dout[  56 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y28"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r8(.clk(clk), .din(din[  64 +: 8]), .dout(dout[  64 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y29"), .INIT0(1'b0), .INIT({256{1'b0}}))
            r9(.clk(clk), .din(din[  72 +: 8]), .dout(dout[  72 +: 8]));
endmodule

module roi_bramds_bit1(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y21"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r1(.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y22"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r2(.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y23"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r3(.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y24"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r4(.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y25"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r5(.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y26"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r6(.clk(clk), .din(din[  48 +: 8]), .dout(dout[  48 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y27"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r7(.clk(clk), .din(din[  56 +: 8]), .dout(dout[  56 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y28"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r8(.clk(clk), .din(din[  64 +: 8]), .dout(dout[  64 +: 8]));
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y29"), .INIT0(1'b1), .INIT({256{1'b0}}))
            r9(.clk(clk), .din(din[  72 +: 8]), .dout(dout[  72 +: 8]));
endmodule

/******************************************************************************
Set all data bits
******************************************************************************/

module roi_bram36_0s(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0({256{1'b0}}), .INIT({256{1'b0}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule

module roi_bram36_1s(input clk, input [255:0] din, output [255:0] dout);
    ram_RAMB36E1 #(.LOC("RAMB36_X0Y20"), .INIT0({256{1'b1}}), .INIT({256{1'b1}}))
            r0(.clk(clk), .din(din[  0 +: 8]), .dout(dout[  0 +: 8]));
endmodule


/******************************************************************************
*******************************************************************************
Library
*******************************************************************************
******************************************************************************/


/*
Site RAMB18_X0Y42
Pushed it outside the pblock
lets extend pblock

for i in xrange(0x08): print '.INITP_%02X(INIT),' % i
for i in xrange(0x40): print '.INIT_%02X(INIT),' % i
*/
module ram_RAMB18E1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    parameter INIT0 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT = 256'h0000000000000000000000000000000000000000000000000000000000000000;

    parameter IS_CLKARDCLK_INVERTED = 1'b0;
    parameter IS_CLKBWRCLK_INVERTED = 1'b0;
    parameter IS_ENARDEN_INVERTED = 1'b0;
    parameter IS_ENBWREN_INVERTED = 1'b0;
    parameter IS_RSTRAMARSTRAM_INVERTED = 1'b0;
    parameter IS_RSTRAMB_INVERTED = 1'b0;
    parameter IS_RSTREGARSTREG_INVERTED = 1'b0;
    parameter IS_RSTREGB_INVERTED = 1'b0;
    parameter RAM_MODE = "TDP";
    parameter WRITE_MODE_A = "WRITE_FIRST";
    parameter WRITE_MODE_B = "WRITE_FIRST";

    parameter DOA_REG = 1'b0;
    parameter DOB_REG = 1'b0;
    parameter SRVAL_A = 18'b0;
    parameter SRVAL_B = 18'b0;
    parameter INIT_A = 18'b0;
    parameter INIT_B = 18'b0;

    parameter READ_WIDTH_A = 0;
    parameter READ_WIDTH_B = 0;
    parameter WRITE_WIDTH_A = 0;
    parameter WRITE_WIDTH_B = 0;

    (* LOC=LOC *)
    RAMB18E1 #(
            .INITP_00(INIT),
            .INITP_01(INIT),
            .INITP_02(INIT),
            .INITP_03(INIT),
            .INITP_04(INIT),
            .INITP_05(INIT),
            .INITP_06(INIT),
            .INITP_07(INIT),

            .INIT_00(INIT0),
            .INIT_01(INIT),
            .INIT_02(INIT),
            .INIT_03(INIT),
            .INIT_04(INIT),
            .INIT_05(INIT),
            .INIT_06(INIT),
            .INIT_07(INIT),
            .INIT_08(INIT),
            .INIT_09(INIT),
            .INIT_0A(INIT),
            .INIT_0B(INIT),
            .INIT_0C(INIT),
            .INIT_0D(INIT),
            .INIT_0E(INIT),
            .INIT_0F(INIT),
            .INIT_10(INIT),
            .INIT_11(INIT),
            .INIT_12(INIT),
            .INIT_13(INIT),
            .INIT_14(INIT),
            .INIT_15(INIT),
            .INIT_16(INIT),
            .INIT_17(INIT),
            .INIT_18(INIT),
            .INIT_19(INIT),
            .INIT_1A(INIT),
            .INIT_1B(INIT),
            .INIT_1C(INIT),
            .INIT_1D(INIT),
            .INIT_1E(INIT),
            .INIT_1F(INIT),
            .INIT_20(INIT),
            .INIT_21(INIT),
            .INIT_22(INIT),
            .INIT_23(INIT),
            .INIT_24(INIT),
            .INIT_25(INIT),
            .INIT_26(INIT),
            .INIT_27(INIT),
            .INIT_28(INIT),
            .INIT_29(INIT),
            .INIT_2A(INIT),
            .INIT_2B(INIT),
            .INIT_2C(INIT),
            .INIT_2D(INIT),
            .INIT_2E(INIT),
            .INIT_2F(INIT),
            .INIT_30(INIT),
            .INIT_31(INIT),
            .INIT_32(INIT),
            .INIT_33(INIT),
            .INIT_34(INIT),
            .INIT_35(INIT),
            .INIT_36(INIT),
            .INIT_37(INIT),
            .INIT_38(INIT),
            .INIT_39(INIT),
            .INIT_3A(INIT),
            .INIT_3B(INIT),
            .INIT_3C(INIT),
            .INIT_3D(INIT),
            .INIT_3E(INIT),
            .INIT_3F(INIT),

            .IS_CLKARDCLK_INVERTED(IS_CLKARDCLK_INVERTED),
            .IS_CLKBWRCLK_INVERTED(IS_CLKBWRCLK_INVERTED),
            .IS_ENARDEN_INVERTED(IS_ENARDEN_INVERTED),
            .IS_ENBWREN_INVERTED(IS_ENBWREN_INVERTED),
            .IS_RSTRAMARSTRAM_INVERTED(IS_RSTRAMARSTRAM_INVERTED),
            .IS_RSTRAMB_INVERTED(IS_RSTRAMB_INVERTED),
            .IS_RSTREGARSTREG_INVERTED(IS_RSTREGARSTREG_INVERTED),
            .IS_RSTREGB_INVERTED(IS_RSTREGB_INVERTED),
            .RAM_MODE(RAM_MODE),
            .WRITE_MODE_A(WRITE_MODE_A),
            .WRITE_MODE_B(WRITE_MODE_B),

            .DOA_REG(DOA_REG),
            .DOB_REG(DOB_REG),
            .SRVAL_A(SRVAL_A),
            .SRVAL_B(SRVAL_B),
            .INIT_A(INIT_A),
            .INIT_B(INIT_B),

            .READ_WIDTH_A(READ_WIDTH_A),
            .READ_WIDTH_B(READ_WIDTH_B),
            .WRITE_WIDTH_A(WRITE_WIDTH_A),
            .WRITE_WIDTH_B(WRITE_WIDTH_B)
        ) ram (
            .CLKARDCLK(din[0]),
            .CLKBWRCLK(din[1]),
            .ENARDEN(din[2]),
            .ENBWREN(din[3]),
            .REGCEAREGCE(din[4]),
            .REGCEB(din[5]),
            .RSTRAMARSTRAM(din[6]),
            .RSTRAMB(din[7]),
            .RSTREGARSTREG(din[0]),
            .RSTREGB(din[1]),
            .ADDRARDADDR(din[2]),
            .ADDRBWRADDR(din[3]),
            .DIADI(din[4]),
            .DIBDI(din[5]),
            .DIPADIP(din[6]),
            .DIPBDIP(din[7]),
            .WEA(din[0]),
            .WEBWE(din[1]),
            .DOADO(dout[0]),
            .DOBDO(dout[1]),
            .DOPADOP(dout[2]),
            .DOPBDOP(dout[3]));

endmodule

module ram_RAMB36E1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter INIT0 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter IS_ENARDEN_INVERTED = 1'b0;

    (* LOC=LOC *)
    RAMB36E1 #(
            .INITP_00(INIT),
            .INITP_01(INIT),
            .INITP_02(INIT),
            .INITP_03(INIT),
            .INITP_04(INIT),
            .INITP_05(INIT),
            .INITP_06(INIT),
            .INITP_07(INIT),
            .INITP_08(INIT),
            .INITP_09(INIT),
            .INITP_0A(INIT),
            .INITP_0B(INIT),
            .INITP_0C(INIT),
            .INITP_0D(INIT),
            .INITP_0E(INIT),
            .INITP_0F(INIT),

            .INIT_00(INIT0),
            .INIT_01(INIT),
            .INIT_02(INIT),
            .INIT_03(INIT),
            .INIT_04(INIT),
            .INIT_05(INIT),
            .INIT_06(INIT),
            .INIT_07(INIT),
            .INIT_08(INIT),
            .INIT_09(INIT),
            .INIT_0A(INIT),
            .INIT_0B(INIT),
            .INIT_0C(INIT),
            .INIT_0D(INIT),
            .INIT_0E(INIT),
            .INIT_0F(INIT),
            .INIT_10(INIT),
            .INIT_11(INIT),
            .INIT_12(INIT),
            .INIT_13(INIT),
            .INIT_14(INIT),
            .INIT_15(INIT),
            .INIT_16(INIT),
            .INIT_17(INIT),
            .INIT_18(INIT),
            .INIT_19(INIT),
            .INIT_1A(INIT),
            .INIT_1B(INIT),
            .INIT_1C(INIT),
            .INIT_1D(INIT),
            .INIT_1E(INIT),
            .INIT_1F(INIT),
            .INIT_20(INIT),
            .INIT_21(INIT),
            .INIT_22(INIT),
            .INIT_23(INIT),
            .INIT_24(INIT),
            .INIT_25(INIT),
            .INIT_26(INIT),
            .INIT_27(INIT),
            .INIT_28(INIT),
            .INIT_29(INIT),
            .INIT_2A(INIT),
            .INIT_2B(INIT),
            .INIT_2C(INIT),
            .INIT_2D(INIT),
            .INIT_2E(INIT),
            .INIT_2F(INIT),
            .INIT_30(INIT),
            .INIT_31(INIT),
            .INIT_32(INIT),
            .INIT_33(INIT),
            .INIT_34(INIT),
            .INIT_35(INIT),
            .INIT_36(INIT),
            .INIT_37(INIT),
            .INIT_38(INIT),
            .INIT_39(INIT),
            .INIT_3A(INIT),
            .INIT_3B(INIT),
            .INIT_3C(INIT),
            .INIT_3D(INIT),
            .INIT_3E(INIT),
            .INIT_3F(INIT),

            .INIT_40(INIT),
            .INIT_41(INIT),
            .INIT_42(INIT),
            .INIT_43(INIT),
            .INIT_44(INIT),
            .INIT_45(INIT),
            .INIT_46(INIT),
            .INIT_47(INIT),
            .INIT_48(INIT),
            .INIT_49(INIT),
            .INIT_4A(INIT),
            .INIT_4B(INIT),
            .INIT_4C(INIT),
            .INIT_4D(INIT),
            .INIT_4E(INIT),
            .INIT_4F(INIT),
            .INIT_50(INIT),
            .INIT_51(INIT),
            .INIT_52(INIT),
            .INIT_53(INIT),
            .INIT_54(INIT),
            .INIT_55(INIT),
            .INIT_56(INIT),
            .INIT_57(INIT),
            .INIT_58(INIT),
            .INIT_59(INIT),
            .INIT_5A(INIT),
            .INIT_5B(INIT),
            .INIT_5C(INIT),
            .INIT_5D(INIT),
            .INIT_5E(INIT),
            .INIT_5F(INIT),
            .INIT_60(INIT),
            .INIT_61(INIT),
            .INIT_62(INIT),
            .INIT_63(INIT),
            .INIT_64(INIT),
            .INIT_65(INIT),
            .INIT_66(INIT),
            .INIT_67(INIT),
            .INIT_68(INIT),
            .INIT_69(INIT),
            .INIT_6A(INIT),
            .INIT_6B(INIT),
            .INIT_6C(INIT),
            .INIT_6D(INIT),
            .INIT_6E(INIT),
            .INIT_6F(INIT),
            .INIT_70(INIT),
            .INIT_71(INIT),
            .INIT_72(INIT),
            .INIT_73(INIT),
            .INIT_74(INIT),
            .INIT_75(INIT),
            .INIT_76(INIT),
            .INIT_77(INIT),
            .INIT_78(INIT),
            .INIT_79(INIT),
            .INIT_7A(INIT),
            .INIT_7B(INIT),
            .INIT_7C(INIT),
            .INIT_7D(INIT),
            .INIT_7E(INIT),
            .INIT_7F(INIT),

            .IS_CLKARDCLK_INVERTED(1'b0),
            .IS_CLKBWRCLK_INVERTED(1'b0),
            .IS_ENARDEN_INVERTED(IS_ENARDEN_INVERTED),
            .IS_ENBWREN_INVERTED(1'b0),
            .IS_RSTRAMARSTRAM_INVERTED(1'b0),
            .IS_RSTRAMB_INVERTED(1'b0),
            .IS_RSTREGARSTREG_INVERTED(1'b0),
            .IS_RSTREGB_INVERTED(1'b0),
            .RAM_MODE("TDP"),
            .WRITE_MODE_A("WRITE_FIRST"),
            .WRITE_MODE_B("WRITE_FIRST"),
            .SIM_DEVICE("VIRTEX6")
        ) ram (
            .CLKARDCLK(din[0]),
            .CLKBWRCLK(din[1]),
            .ENARDEN(din[2]),
            .ENBWREN(din[3]),
            .REGCEAREGCE(din[4]),
            .REGCEB(din[5]),
            .RSTRAMARSTRAM(din[6]),
            .RSTRAMB(din[7]),
            .RSTREGARSTREG(din[0]),
            .RSTREGB(din[1]),
            .ADDRARDADDR(din[2]),
            .ADDRBWRADDR(din[3]),
            .DIADI(din[4]),
            .DIBDI(din[5]),
            .DIPADIP(din[6]),
            .DIPBDIP(din[7]),
            .WEA(din[0]),
            .WEBWE(din[1]),
            .DOADO(dout[0]),
            .DOBDO(dout[1]),
            .DOPADOP(dout[2]),
            .DOPBDOP(dout[3]));
endmodule

