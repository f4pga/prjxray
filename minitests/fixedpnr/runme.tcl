
create_project -force -part $::env(XRAY_PART) design_fdre design_fdre
read_verilog top_fdre.v

synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports ce]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports sr]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports d]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_04) IOSTANDARD LVCMOS33" [get_ports q]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

place_design
route_design

set_property IS_ROUTE_FIXED 1 [get_nets -hierarchical]
set_property IS_LOC_FIXED 1 [get_cells -hierarchical]
set_property IS_BEL_FIXED 1 [get_cells -hierarchical]

write_xdc -force fixed.xdc

write_checkpoint -force design_fdre.dcp
write_bitstream -force design_fdre.bit

close_project

foreach variant {fdse fdce fdce_inv fdpe ldce ldpe} {
	create_project -force -part $::env(XRAY_PART) design_${variant} design_${variant}
	read_verilog top_${variant}.v
	read_xdc fixed.xdc

	synth_design -top top
	place_design
	route_design

	write_checkpoint -force design_${variant}.dcp
	write_bitstream -force design_${variant}.bit

	close_project
}

