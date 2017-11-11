
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

proc putl {lst} {
	foreach line $lst {puts $line}
}

