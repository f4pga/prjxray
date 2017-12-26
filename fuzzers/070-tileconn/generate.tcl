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

source ../../../utils/utils.tcl

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

set tiles [roi_tiles]
set horz_cache [dict create]
set vert_cache [dict create]

set fp [open "tilepairs.txt" w]
foreach tile $tiles {
	set tile_type [get_property TILE_TYPE $tile]
	set grid_x [get_property GRID_POINT_X $tile]
	set grid_y [get_property GRID_POINT_Y $tile]

	set horz_tile [get_tiles -filter "GRID_POINT_X == [expr $grid_x + 1] && GRID_POINT_Y == $grid_y"]
	set vert_tile [get_tiles -filter "GRID_POINT_Y == [expr $grid_y + 1] && GRID_POINT_X == $grid_x"]

	set horz_type [get_property TILE_TYPE $horz_tile]
	set vert_type [get_property TILE_TYPE $vert_tile]

	if {! [dict exists $horz_cache $tile_type.$horz_type]} {
		dict append horz_cache $tile_type.$horz_type
		print_tile_pair $fp $tile $horz_tile
	}

	if {! [dict exists $vert_cache $tile_type.$vert_type]} {
		dict append vert_cache $tile_type.$vert_type
		print_tile_pair $fp $tile $vert_tile
	}
}
close $fp

