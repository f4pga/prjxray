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

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets o_OBUF]

place_design
route_design

write_checkpoint -force design.dcp

source ../../../utils/utils.tcl

proc write_txtdata {filename} {
	puts "Writing $filename."
	set fp [open $filename w]
	set all_pips [lsort -unique [get_pips -of_objects [get_nets -hierarchical]]]
	if {$all_pips != {}} {
		puts "Dumping pips."
		foreach tile [get_tiles [regsub -all {CLBL[LM]} [get_tiles -of_objects [get_sites -of_objects [get_pblocks roi]]] INT]] {
			foreach pip [filter $all_pips "TILE == $tile"] {
				set src_wire [get_wires -uphill -of_objects $pip]
				set dst_wire [get_wires -downhill -of_objects $pip]
				set num_pips [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]]
				set dir_prop [get_property IS_DIRECTIONAL $pip]
				puts $fp "$tile $pip $src_wire $dst_wire $num_pips $dir_prop"
			}
		}
	}
	close $fp
}

set int_l_tiles [filter [pblock_tiles roi] {TYPE == INT_L}]
set int_r_tiles [filter [pblock_tiles roi] {TYPE == INT_R}]

set fp [open "../todo.txt" r]
set todo_lines {}
for {gets $fp line} {$line != ""} {gets $fp line} {
	lappend todo_lines $line
}
close $fp

for {set i 100} {$i < 200} {incr i} {
	set route_nodes {}
	foreach line [randsample_list 5 $todo_lines] {
		set line [split $line .]
		set tile_type [lindex $line 0]
		set dst_wire [lindex $line 1]
		set src_wire [lindex $line 2]

		set tile ""
		if {$tile_type == "INT_L"} {
			set j [expr {int(rand()*[llength $int_l_tiles])}]
			set tile [lindex $int_l_tiles $j]
		}
		if {$tile_type == "INT_R"} {
			set j [expr {int(rand()*[llength $int_r_tiles])}]
			set tile [lindex $int_r_tiles $j]
		}

		lappend route_nodes $tile/$src_wire
		lappend route_nodes $tile/$dst_wire
	}

	set_property FIXED_ROUTE {} [get_nets o_OBUF]
	route_design -unroute -net [get_nets o_OBUF]
	route_via o_OBUF $route_nodes

	write_bitstream -quiet -force design_$i.bit
	write_txtdata design_$i.txt
}

