create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports a]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports y]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

write_checkpoint -force design.dcp
# write_bitstream -force design.bit

proc print_tile_pair {fp t1 t2} {
	set t1 [get_tiles $t1]
	set t2 [get_tiles $t2]

	puts "Checking $t1 against $t2."

	set t1_nodes [lsort -unique [get_nodes -quiet -of_objects [get_wires -of_objects $t1]]]
	set t2_nodes [lsort -unique [get_nodes -quiet -of_objects [get_wires -of_objects $t2]]]
	set nodes {}

	foreach node $t1_nodes {
		if {$node in $t2_nodes} {
			lappend nodes $node
		}
	}

	foreach node $nodes {
		set t1_wires [get_wires -quiet -filter "TILE_NAME == $t1" -of_objects $node]
		set t2_wires [get_wires -quiet -filter "TILE_NAME == $t2" -of_objects $node]
		foreach w1 $t1_wires {
			foreach w2 $t2_wires {
				puts $fp "$w1 $w2"
			}
		}
	}
}

proc print_tile_pairs {fp lst} {
	for {set i 1} {$i < [llength $lst]} {incr i} {
		print_tile_pair $fp [lindex $lst [expr $i - 1]] [lindex $lst $i]
	}
}

set fp [open "tilepairs.txt" w]
if {$::env(XRAY_DATABASE) == "artix7"} {
	# horizontal pairs
	print_tile_pairs $fp "INT_R_X13Y114 CLBLL_R_X13Y114 CLBLL_L_X14Y114 INT_L_X14Y114 INT_R_X15Y114"
	print_tile_pairs $fp "VBRK_X29Y125 CLBLM_L_X10Y120 INT_L_X10Y120 INT_R_X11Y120 CLBLM_R_X11Y120 VBRK_X34Y125 CLBLL_L_X12Y120"
	print_tile_pairs $fp "CLBLL_R_X17Y113 VFRAME_X47Y118"
	print_tile_pairs $fp "HCLK_VBRK_X29Y130 HCLK_CLB_X30Y130 HCLK_L_X31Y130 HCLK_R_X32Y130 HCLK_CLB_X33Y130 HCLK_VBRK_X34Y130 HCLK_CLB_X35Y130"
	print_tile_pairs $fp "HCLK_CLB_X46Y130 HCLK_VFRAME_X47Y130"
	print_tile_pairs $fp "T_TERM_INT_X31Y156 T_TERM_INT_X32Y156"
	print_tile_pairs $fp "BRKH_CLB_X10Y99 BRKH_INT_X10Y99 BRKH_INT_X11Y99 BRKH_CLB_X11Y99"
	print_tile_pairs $fp "BRKH_B_TERM_INT_X36Y104 BRKH_B_TERM_INT_X37Y104"

	# vertical pairs
	print_tile_pairs $fp "CLBLM_L_X10Y115 CLBLM_L_X10Y114"
	print_tile_pairs $fp "INT_L_X10Y115 INT_L_X10Y114"
	print_tile_pairs $fp "INT_R_X11Y115 INT_R_X11Y114"
	print_tile_pairs $fp "CLBLM_R_X11Y115 CLBLM_R_X11Y114"
	print_tile_pairs $fp "VBRK_X34Y120 VBRK_X34Y119"
	print_tile_pairs $fp "CLBLL_L_X12Y115 CLBLL_L_X12Y114"
	print_tile_pairs $fp "CLBLL_R_X13Y115 CLBLL_R_X13Y115"
	print_tile_pairs $fp "VFRAME_X47Y120 VFRAME_X47Y119"
	print_tile_pairs $fp "T_TERM_INT_X31Y156 INT_L_X10Y149"
	print_tile_pairs $fp "T_TERM_INT_X32Y156 INT_R_X11Y149"
	print_tile_pairs $fp "CLBLM_L_X10Y100 BRKH_CLB_X10Y99"
	print_tile_pairs $fp "INT_L_X10Y100 BRKH_INT_X10Y99"
	print_tile_pairs $fp "INT_R_X11Y100 BRKH_INT_X11Y99"
	print_tile_pairs $fp "CLBLM_R_X11Y100 BRKH_CLB_X11Y99"
	print_tile_pairs $fp "INT_L_X12Y100 BRKH_B_TERM_INT_X36Y104"
	print_tile_pairs $fp "INT_R_X13Y100 BRKH_B_TERM_INT_X37Y104"
}
close $fp

