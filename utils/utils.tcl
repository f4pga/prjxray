# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
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

# returns list of unique tile types
proc get_tile_types {} {
    set all_tiles [get_tiles]
    set types {}
    foreach tile $all_tiles {
        set type [get_property TYPE $tile]
        #ignore empty tiles
        if {$type == "NULL"} { continue }
        if {[lsearch -exact $types $type] == -1} {lappend types $type}
    }
    return $types
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

proc write_pip_txtdata {filename} {
    puts "FUZ([pwd]): Writing $filename."
    set fp [open $filename w]
    set nets [get_nets -hierarchical]
    set nnets [llength $nets]
    set neti 0
    foreach net $nets {
        incr neti
        if {($neti % 100) == 0 } {
            puts "FUZ([pwd]): Dumping pips from net $net ($neti / $nnets)"
        }
        foreach pip [get_pips -of_objects $net] {
            set tile [get_tiles -of_objects $pip]
            set src_wire [get_wires -uphill -of_objects $pip]
            set dst_wire [get_wires -downhill -of_objects $pip]
            set num_pips [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]]
            set dir_prop [get_property IS_DIRECTIONAL $pip]
            puts $fp "$tile $pip $src_wire $dst_wire $num_pips $dir_prop"
        }
    }
    close $fp
}

# Generic non-ROI'd generate.tcl template
proc generate_top {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

# Dumps all pins of a site, with the direction info (clock, input, output)
proc dump_pins {file_name site_prefix} {
    set fp [open $file_name w]

    puts $fp "name,is_input,is_output,is_clock"
    set site [lindex [get_sites $site_prefix*] 0]
    set bel [get_bels -of_objects $site]
    set bel_pins [get_bel_pins -of_objects $bel]

    set bel_pins_dict [dict create]
    foreach pin $bel_pins {
        set pin_name [lindex [split $pin "/"] 2]
        set is_clock [get_property IS_CLOCK $pin]
        dict set bel_pins_dict $pin_name $is_clock
    }

    set site_pins [get_site_pins -of_objects $site]
    foreach pin $site_pins {
        set connected_pip [get_pips -of_objects [get_nodes -of_objects $pin]]

        if { $connected_pip == "" } {
            continue
        }

        set pin_name [lindex [split $pin "/"] 1]
        set is_input [get_property IS_INPUT $pin]
        set is_output [get_property IS_OUTPUT $pin]
        set is_clock [dict get $bel_pins_dict $pin_name]

        puts $fp "$pin_name,$is_input,$is_output,$is_clock"
    }
    close $fp
}
