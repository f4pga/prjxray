create_project -force -part $::env(XRAY_PART) piplist piplist

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
route_design

write_checkpoint -force piplist.dcp

source ../../utils/utils.tcl

proc print_tile_pips {tile_type filename} {
	set tile [lindex [get_tiles -filter "TYPE == $tile_type"] 0]
	puts "Dumping and PIPs for tile $tile ($tile_type) to $filename."
	set fp [open $filename w]
	foreach pip [lsort [get_pips -filter {IS_DIRECTIONAL} -of_objects [get_tiles $tile]]] {
		set src [get_wires -uphill -of_objects $pip]
		set dst [get_wires -downhill -of_objects $pip]
		if {[llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst]]] != 1} {
			puts $fp "$tile_type.[regsub {.*/} $dst ""].[regsub {.*/} $src ""]"
		}
	}
	close $fp
}

print_tile_pips INT_L pips_int_l.txt
print_tile_pips INT_R pips_int_r.txt

