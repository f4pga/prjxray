proc route_via { net nodes {assert 1} } {
    # Route a simple source to dest net via one or more intermediate nodes
    # the nodes do not have have to be directly reachable from each other
    # net: net name string
    # nodes: list of node or wires strings?
    # Returns 1 on success (previously would silently failed with antenna nets)

    set net [get_nets $net]
    # fixed_route: list of nodes in the full route
    # Begins at implicit node
    set fixed_route [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
    # Implicit end node. Route it at the end
    lappend nodes [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]]

    puts "Routing net $net:"

    foreach to_node $nodes {
        # convert wire string to node object
        set to_node [get_nodes -of_objects [get_wires $to_node]]
        # Start at the last point
        set from_node [lindex $fixed_route end]
        # Make vivado do the hard work
        puts "  set route \[find_routing_path -quiet -from $from_node -to $to_node\]"
        set route [find_routing_path -quiet -from $from_node -to $to_node]
        # TODO: check for this
        if {$route == ""} {
            # This can also happen if you try to route to a node already in the route
            if { [ lsearch $route $to_node ] >= 0 } {
                puts "  WARNING: route_via loop. $to_node is already in the path, ignoring"
            } else {
                puts "  $from_node -> $to_node: no route found - assuming direct PIP"
                lappend fixed_route $to_node
            }
        } {
            puts "  $from_node -> $to_node: $route"
            set fixed_route [concat $fixed_route [lrange $route 1 end]]
        }
        set_property -quiet FIXED_ROUTE $fixed_route $net
    }

    # Earlier check should catch this now
    set status [get_property ROUTE_STATUS $net]
    if { $status != "ROUTED" } {
        puts "  Failed to route net $net, status $status, route: $fixed_route"
        if { $assert } {
            error "Failed to route net"
        }
        return 0
    }

    set_property -quiet FIXED_ROUTE $fixed_route $net
    puts ""
    return 1
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

proc roi_tiles {} {
	return [get_tiles -filter "GRID_POINT_X >= $::env(XRAY_ROI_GRID_X1) && \
			GRID_POINT_X < $::env(XRAY_ROI_GRID_X2) && \
			GRID_POINT_Y >= $::env(XRAY_ROI_GRID_Y1) && \
            GRID_POINT_Y < $::env(XRAY_ROI_GRID_Y2)"]
}

proc pblock_tiles {pblock} {
    set clb_tiles [get_tiles -of_objects [get_sites -of_objects [get_pblocks $pblock]]]
    set int_tiles [get_tiles [regsub -all {CLBL[LM]} $clb_tiles INT]]
    return [get_tiles "$clb_tiles $int_tiles"]
}

proc lintersect {lst1 lst2} {
    set rlst {}
    foreach el $lst1 {
        set idx [lsearch $lst2 $el]
        if {$idx >= 0} {lappend rlst $el}
    }
    return $rlst
}

proc putl {lst} {
    foreach line $lst {puts $line}
}
