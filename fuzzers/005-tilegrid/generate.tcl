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

set luts [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ LUT*} */A6LUT]
set selected_luts {}
set lut_index 0

if 0 {
	set grid_min_x -1
	set grid_max_x -1
	set grid_min_y -1
	set grid_max_y -1
} {
	set grid_min_x $::env(XRAY_ROI_GRID_X1)
	set grid_max_x $::env(XRAY_ROI_GRID_X2)
	set grid_min_y $::env(XRAY_ROI_GRID_Y1)
	set grid_max_y $::env(XRAY_ROI_GRID_Y2)
}

# LOC one LUT (a "selected_lut") into each CLB segment configuration column (ie 50 per column)
# Also, if GRID_MIN/MAX is not defined, automatically create it based on used CLBs
# See caveat in README on automatic creation
foreach lut $luts {
	set tile [get_tile -of_objects $lut]
	set grid_x [get_property GRID_POINT_X $tile]
	set grid_y [get_property GRID_POINT_Y $tile]

	if [expr $grid_min_x < 0 || $grid_x < $grid_min_x] {set grid_min_x $grid_x}
	if [expr $grid_max_x < 0 || $grid_x > $grid_max_x] {set grid_max_x $grid_x}

	if [expr $grid_min_y < 0 || $grid_y < $grid_min_y] {set grid_min_y $grid_y}
	if [expr $grid_max_y < 0 || $grid_y > $grid_max_y] {set grid_max_y $grid_y}

	# 50 per column => 50, 100, 150, etc
	if [regexp "Y(0|[0-9]*[05]0)/" $lut] {
		set cell [get_cells roi/is[$lut_index].lut]
		set_property LOC [get_sites -of_objects $lut] $cell
		set lut_index [expr $lut_index + 1]
		lappend selected_luts $lut
	}
}

place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

# Get all tiles in ROI, ie not just the selected LUTs
set tiles [get_tiles -filter "GRID_POINT_X >= $grid_min_x && GRID_POINT_X <= $grid_max_x && GRID_POINT_Y >= $grid_min_y && GRID_POINT_Y <= $grid_max_y"]

# Write tiles.txt with site metadata
set fp [open "tiles.txt" w]
foreach tile $tiles {
	set type [get_property TYPE $tile]
	set grid_x [get_property GRID_POINT_X $tile]
	set grid_y [get_property GRID_POINT_Y $tile]
	set sites [get_sites -quiet -of_objects $tile]
	set typed_sites {}

	if [llength $sites] {
		set site_types [get_property SITE_TYPE $sites]
		foreach t $site_types s $sites {
			lappend typed_sites $t $s
		}
	}

	puts $fp "$type $tile $grid_x $grid_y $typed_sites"
}
close $fp

# Toggle one bit in each selected LUT to generate base addresses
for {set i 0} {$i < $lut_index} {incr i} {
	set cell [get_cells roi/is[$i].lut]
	set orig_init [get_property INIT $cell]
	# Flip a bit by changing MSB 0 => 1
	set new_init [regsub "h8" $orig_init "h0"]
	set_property INIT $new_init $cell
	write_bitstream -force design_[get_sites -of_objects [lindex $selected_luts $i]].bit
	set_property INIT $orig_init $cell
}

