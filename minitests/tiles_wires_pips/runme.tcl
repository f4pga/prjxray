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
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

source ../../utils/utils.tcl

proc print_tile_info {tile} {
	puts "Dumping wires and PIPs for tile $tile."
	set fp [open "wires_${tile}.txt" w]
	foreach wire [lsort [get_wires -of_objects [get_tiles $tile]]] {
		puts $fp [regsub {.*/} $wire ""]
	}
	close $fp
	set fp [open "pips_${tile}.txt" w]
	foreach wire [lsort [get_pips -of_objects [get_tiles $tile]]] {
		puts $fp [regsub {.*/} $wire ""]
	}
	close $fp
}

foreach tile [lsort [get_tiles]] {
	print_tile_info $tile
}

