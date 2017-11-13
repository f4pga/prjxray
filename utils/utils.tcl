
proc route_via {net nodes} {
	set net [get_nets $net]
	set fixed_route [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
	lappend nodes [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]]

	puts ""
	puts "Routing net $net:"

	foreach to_node $nodes {
		set to_node [get_nodes -of_objects [get_wires $to_node]]
		set from_node [lindex $fixed_route end]
		set route [find_routing_path -quiet -from $from_node -to $to_node]
		if {$route == ""} {
			puts "  $from_node -> $to_node: no route found - assuming direct PIP"
			lappend fixed_route $to_node
		} {
			puts "  $from_node -> $to_node: $route"
			set fixed_route [concat $fixed_route [lrange $route 1 end]]
		}
	}

	set_property FIXED_ROUTE $fixed_route $net
	puts ""
}

proc tile_wire_pairs {tile1 tile2} {
	set tile1 [get_tiles $tile1]
	set tile2 [get_tiles $tile2]

	foreach wire1 [lsort [get_wires -of_objects $tile1]] {
		set wire2 [get_wires -quiet -filter "TILE_NAME == $tile2" -of_objects [get_nodes -quiet -of_objects $wire1]]
		if {$wire2 != ""} {puts "$wire1 $wire2"}
	}
}

proc randsample_list {num lst} {
	set rlst {}
	for {set i 0} {$i<$num} {incr i} {
		set j [expr {int(rand()*[llength $lst])}]
		lappend rlst [lindex $lst $j]
		set lst [lreplace $lst $j $j]
	}
	return $rlst
}

proc randplace_pblock {num pblock} {
	set sites [randsample_list $num [get_sites -filter {SITE_TYPE == SLICEL || SITE_TYPE == SLICEM} -of_objects [get_pblocks $pblock]]]
	set cells [randsample_list $num [get_cells -hierarchical -filter "PBLOCK == [get_pblocks $pblock] && REF_NAME == LUT6"]]
	for {set i 0} {$i<$num} {incr i} {
		set site [lindex $sites $i]
		set cell [lindex $cells $i]
		set_property LOC $site $cell
	}
}

proc putl {lst} {
	foreach line $lst {puts $line}
}

