create_project -force -part $::env(XRAY_PART) design design

read_verilog top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports a]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports b]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports c]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports x]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_04) IOSTANDARD LVCMOS33" [get_ports y]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_05) IOSTANDARD LVCMOS33" [get_ports z]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

source ../../utils/utils.tcl
source pips.tcl
source routes.tcl

