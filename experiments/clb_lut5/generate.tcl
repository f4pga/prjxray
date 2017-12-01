create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells roi]
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit


# Get all 6LUT and 5LUT in pblock
# A6LUT, B6LUT, A5LUT, etc
set luts [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ LUT*} */*LUT]

set grid_min_x -1
set grid_max_x -1
set grid_min_y -1
set grid_max_y -1

foreach lut $luts {
	set tile [get_tile -of_objects $lut]
	set grid_x [get_property GRID_POINT_X $tile]
	set grid_y [get_property GRID_POINT_Y $tile]

	if [expr $grid_min_x < 0 || $grid_x < $grid_min_x] {set grid_min_x $grid_x}
	if [expr $grid_max_x < 0 || $grid_x > $grid_max_x] {set grid_max_x $grid_x}

	if [expr $grid_min_y < 0 || $grid_y < $grid_min_y] {set grid_min_y $grid_y}
	if [expr $grid_max_y < 0 || $grid_y > $grid_max_y] {set grid_max_y $grid_y}
}

set fp [open "design.txt" w]
foreach lut $luts {
	if [get_property IS_USED $lut] {
	    set tile [get_tile -of_objects $lut]
	    set grid_x [get_property GRID_POINT_X $tile]
	    set grid_y [get_property GRID_POINT_Y $tile]
	    set type [get_property TYPE $tile]
	    set lut_type [get_property TYPE $lut]
	    set lutc [get_cells -of_objects $lut]
	    set cell_bel [get_property BEL $lutc]

		puts $fp "$type $tile $grid_x $grid_y $lut $lut_type $cell_bel"
	}
}
close $fp

