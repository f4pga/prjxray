create_project -force -part $::env(XRAY_PART) design design

read_verilog top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports i]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports o]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

place_design
source ../../utils/utils.tcl

# ----------------------------------------------------------

set_property FIXED_ROUTE {} [get_nets o_OBUF]
route_design -unroute

route_via o_OBUF {
	INT_L_X12Y144/LVB_L12 INT_L_X12Y132/LVB_L12

	INT_L_X12Y120/SS6BEG2
	INT_L_X14Y120/NN6END3

	INT_L_X14Y132/LVB_L12 INT_L_X14Y144/LVB_L12
	INT_L_X16Y144/LVB_L12 INT_L_X16Y132/LVB_L12
}

# ----------------------------------------------------------

route_design
write_checkpoint -force design_a.dcp
write_bitstream -force design_a.bit

# ----------------------------------------------------------

set_property FIXED_ROUTE {} [get_nets o_OBUF]
route_design -unroute

route_via o_OBUF {
	INT_L_X12Y120/NN6END3

	INT_L_X12Y132/LVB_L12 INT_L_X12Y144/LVB_L12

	INT_L_X14Y144/LVB_L12 INT_L_X14Y132/LVB_L12

	INT_L_X14Y120/SS6BEG2
	INT_L_X16Y120/NN6END3

	INT_L_X16Y132/LVB_L12 INT_L_X16Y144/LVB_L12

	INT_L_X16Y144/EE4BEG2
}

# ----------------------------------------------------------

route_design
write_checkpoint -force design_b.dcp
write_bitstream -force design_b.bit

