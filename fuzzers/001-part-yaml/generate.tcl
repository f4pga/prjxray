create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_param tcl.collectionResultDisplayLimit 0

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

place_design
route_design

write_checkpoint -force design.dcp

# Write a normal bitstream that will do a singe FDRI write of all the frames.
write_bitstream -force design.bit

# Write a perframecrc bitstream which writes each frame individually followed by
# the frame address.  This shows where there are gaps in the frame address
# space.
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
write_bitstream -force design.perframecrc.bit
set_property BITSTREAM.GENERAL.PERFRAMECRC NO [current_design]
