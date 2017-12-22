create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports i]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports o]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

# write_checkpoint -force design.dcp

source ../../../utils/utils.tcl

set fp [open "../todo.txt" r]
set todo_lines {}
for {gets $fp line} {$line != ""} {gets $fp line} {
	lappend todo_lines [split $line .]
}
close $fp

set int_l_tiles [randsample_list [llength $todo_lines] [filter [pblock_tiles roi] {TYPE == INT_L}]]
set int_r_tiles [randsample_list [llength $todo_lines] [filter [pblock_tiles roi] {TYPE == INT_R}]]

set fp [open "design.txt" w]

for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
	set line [lindex $todo_lines $idx]
	puts "== $idx: $line"

	set tile_type [lindex $line 0]
	set dst_wire [lindex $line 1]
	set src_wire [lindex $line 2]

	if {$tile_type == "INT_L"} {set tile [lindex $int_l_tiles $idx]; set other_tile [lindex $int_r_tiles $idx]}
	if {$tile_type == "INT_R"} {set tile [lindex $int_r_tiles $idx]; set other_tile [lindex $int_l_tiles $idx]}

	puts "PIP Tile: $tile"

	set driver_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
			-of_objects [get_nodes -of_objects [get_wires $other_tile/CLK*0]]]]]

	puts "LUT Tile (Site): $other_tile ($driver_site)"

	set mylut [create_cell -reference LUT1 mylut_$idx]
	set_property -dict "LOC $driver_site BEL A6LUT" $mylut

	set mynet [create_net mynet_$idx]
	connect_net -net $mynet -objects "$mylut/I0 $mylut/O"
	route_via $mynet "$tile/$src_wire $tile/$dst_wire"

	if {[get_pips -filter "NAME == \"${tile}/${tile_type}.${src_wire}<<->>${dst_wire}\" || NAME == \"${tile}/${tile_type}.${dst_wire}<<->>${src_wire}\""  -of_objects [get_nets $mynet]] != ""} {
		puts $fp "A $tile/$dst_wire $tile/$src_wire"
	}
}

route_design

set all_pips [lsort -unique [get_pips -of_objects [get_nets -hierarchical]]]
foreach tile [get_tiles [regsub -all {CLBL[LM]} [get_tiles -of_objects [get_sites -of_objects [get_pblocks roi]]] INT]] {
	foreach pip [filter $all_pips "TILE == $tile"] {
		puts $fp "B [get_wires -of_objects $pip]"
	}
}

close $fp

write_checkpoint -force design.dcp
write_bitstream -force design.bit

