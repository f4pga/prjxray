create_project -force -part $::env(XRAY_PART) design design

read_verilog top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports c]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports d]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports q]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets c_IBUF]

place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

source ../../utils/utils.tcl

foreach it {
	{b11 INT_L_X12Y100/GCLK_L_B11}
	{b10 INT_L_X12Y100/GCLK_L_B10}
	{b9  INT_L_X12Y100/GCLK_L_B9}
	{b8  INT_L_X12Y100/GCLK_L_B8}
	{b7  INT_L_X12Y100/GCLK_L_B7}
	{b6  INT_L_X12Y100/GCLK_L_B6}
	{b5  INT_R_X13Y100/GCLK_B5}
	{b4  INT_R_X13Y100/GCLK_B4}
	{b3  INT_R_X13Y100/GCLK_B3}
	{b2  INT_R_X13Y100/GCLK_B2}
	{b1  INT_R_X13Y100/GCLK_B1}
	{b0  INT_R_X13Y100/GCLK_B0}
} {
	set net [get_nets c_IBUF_BUFG]
	set_property FIXED_ROUTE {} $net
	route_design -unroute -net $net

	set id [lindex $it 0]
	set gclk [lindex $it 1]

	route_via $net "$gclk"

	write_checkpoint -force design_$id.dcp
	write_bitstream -force design_$id.bit
}

