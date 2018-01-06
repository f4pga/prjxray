Some quick tests to understand BRAM configuration
Written before segments were fully developed, so this preliminary writeup is a bit coarse

Basically all the RAMB36 configuration tests show two bit flips
This indicates that RAMB18 and RAMB36 are fully indepdnently configurable
SDP vs TDP was a lot more complicated, needs more investigation

Note: tested on a7 after sourcing env.sh. k7 would likely also work


Raw data

set_property LOC RAMB36_X0Y21 [get_cells ram]

design_CLKARDCLK_INV.bits
  < bit_0002031b_013_11
  < bit_0002031b_016_21

design_CLKBWRCLK_INV.bits
  < bit_0002031b_013_13
  < bit_0002031b_016_19

design_CLKARDCLK_INV.bits
  < bit_0002031b_013_11
  < bit_0002031b_016_21

design_CLKBWRCLK_INV.bits
  < bit_0002031b_013_13
  < bit_0002031b_016_19

design_ENARDEN_INV.bits
  < bit_0002031b_013_16
  < bit_0002031b_016_16

design_ENBWREN_INV.bits
  < bit_0002031b_013_19
  < bit_0002031b_016_13

design_RSTRAMARSTRAM_INV.bits
  < bit_0002031b_013_20
  < bit_0002031b_016_12

design_RSTRAMB_INV.bits
  < bit_0002031b_013_21
  < bit_0002031b_016_11

design_RSTREGARSTREG_INV.bits
  < bit_0002031b_013_24
  < bit_0002031b_016_08

design_RSTREGB_INV.bits
  < bit_0002031b_013_27
  < bit_0002031b_016_05

design_WRITE_MODE_A_NC.bits
  > bit_0002031b_012_00
  > bit_0002031b_018_00

design_WRITE_MODE_A_RF.bits
  > bit_0002031b_011_24
  > bit_0002031b_018_08

TDP vs SDP probably does routing changes, leading to a lot of bit flips
design_RAM_MODE_SDP.bits
  > bit_00020282_010_05
  > bit_00020284_010_06
  < bit_00020289_010_04
  < bit_0002028f_010_04
  > bit_00020300_014_11
  < bit_00020300_016_27
  > bit_00020300_016_25
...etc
