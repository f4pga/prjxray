# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc load_todo {{dir "dst"}} {
    set fp [open "../../todo_all.txt" r]

    # Create map of pip source to remaining destinations for that pip
    set todo_map [dict create]
    for {gets $fp line} {$line != ""} {gets $fp line} {
        set parts [split $line .]
        if {$dir == "dsts"} {
            dict lappend todo_map [lindex $parts 2] [list [lindex $parts 0] [lindex $parts 1]]
        } elseif {$dir == "srcs"} {
            dict lappend todo_map [lindex $parts 1] [list [lindex $parts 0] [lindex $parts 2]]
        } else {
            error "Incorrect argument. Available options: src, dst"
        }
    }
    close $fp
    return $todo_map
}

proc shuffle_list {list} {
    set l [llength $list]
    for {set i 0} {$i<=$l} {incr i} {
        set x [lindex $list [set p [expr {int(rand()*$l)}]]]
        set list [lreplace $list $p $p]
        set list [linsert $list [expr {int(rand()*$l)}] $x]
    }

    return $list
}

# Get the dictionary of nets with one corresponding source wire
# of a PIP from the todo list
proc get_nets_with_todo_pip_wires {direction net_regexp wire_regexp {verbose false}} {
    set todo_map [load_todo $direction]
    set nets [get_nets]
    set todo_nets [dict create]

    foreach net $nets {
        if {![regexp $net_regexp $net]} {
            continue
        }
        # Check to see if this net is one we are interested in*
        set wires [get_wires -of_objects $net -filter {TILE_NAME =~ "*GTP_COMMON_MID*" && NAME =~ "*CK_IN*"} -quiet]

        set wire_found 0
        foreach wire $wires {
            if [regexp $wire_regexp $wire] {
                set wire_found 1
                break
            }
        }

        if {$wire_found == 0} {
            if {$verbose} {
                puts "$net not going to a GTP common wire, skipping."
            }
            continue
        }

        set tile [lindex [split $wire /] 0]
        set wire [lindex [split $wire /] 1]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]

        dict set todo_nets $net [list $tile $wire]
    }

    return $todo_nets
}

proc route_todo {} {
    set verbose false

    set used_destinations [dict create]

    # Re-route CMT-related nets, which are originated from the fabric's PLL/MMCM primitives
    set todo_map [load_todo "srcs"]
    set pll_nets [get_nets_with_todo_pip_wires "srcs" "pll_clock" "HCLK_GTP_CK_IN" $verbose]
    set mmcm_nets [get_nets_with_todo_pip_wires "srcs" "mmcm_clock" "HCLK_GTP_CK_IN" $verbose]
    set cmt_nets [dict merge $pll_nets $mmcm_nets]
    puts "CMT nets: $cmt_nets"
    dict for {net tile_wire} $cmt_nets {
        route_design -unroute -nets $net
    }

    dict for {net tile_wire} $cmt_nets {
        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set dsts [dict keys $todo_map]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]
        set todos {}

        # All clock nets which have a source belonging to a PLL/MMCM tile can be routed to any
        # HCLK_GTP_CK_MUX --> HCLK_GTP_CK_IN wire pair, hence we build a list of all the remaining
        # PIPs to choose from.
        puts "Rerouting net $net at $tile / $wire (type $tile_type)"

        foreach dst $dsts {
            set srcs [dict get $todo_map $dst]
            foreach src $srcs {
                # For each HCLK_GTP_CK_IN wire, get the source node (HCLK_GTP_CK_MUX) from the todo_map
                # that still needs to be documented.
                #
                # Each HCLK_GTP_CK_IN has two possible HCLK_GTP_CK_MUX sources to be paired with.
                set src_wire [lindex $src 1]

                set wire_pairs [list $src_wire $dst]
                lappend todos $wire_pairs
            }
        }

        set todos_length [llength $todos]
        if {$todos_length == 0} {
            continue
        }

        puts "All todos for $tile_type / $wire"
        foreach src_wire $todos {
            puts "  - $src_wire"
        }

        set todos [shuffle_list $todos]

        set target_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]]
        puts "Target node: $target_node"
        route_design -unroute -nets $net

        # Find an output in the todo list that can drive.
        foreach wire_pair $todos {

            set src_wire [lindex $wire_pair 0]
            set dst_wire [lindex $wire_pair 1]

            set used_dst_wire [dict exists $used_destinations "$tile/$dst_wire"]
            set used_src_wire [dict exists $used_destinations "$tile/$src_wire"]

            # If one between MUX or IN wire pairs is already used, skip this todo
            if { $used_dst_wire || $used_src_wire } {
                puts "Not routing to $tile / $src_wire or $dst_wire, in use."
                continue
            }

            set origin_src_wire [get_wires "$tile/$src_wire"]
            set origin_src_node [get_nodes -of_objects $origin_src_wire]
            if {[llength $origin_src_node] == 0} {
                error "Failed to find node for $tile/$src_wire."
            }

            set origin_dst_wire [get_wires "$tile/$dst_wire"]
            set origin_dst_node [get_nodes -of_objects $origin_dst_wire]
            if {[llength $origin_dst_node] == 0} {
                error "Failed to find node for $tile/$dst_wire."
            }

            # Route the net through the desired node
            puts "Attempting to route to $src_wire and $dst_wire for net $net."
            route_via $net [list $origin_src_node $origin_dst_node]

            puts "Target node: $target_node"
            puts "Origin src wire: $origin_src_wire"
            puts "Origin src node: $origin_src_node"
            puts "Origin dst wire: $origin_dst_wire"
            puts "Origin dst node: $origin_dst_node"

            dict set used_destinations "$origin_dst_wire" 1
            dict set used_destinations "$origin_src_wire" 1

            break
        }
    }
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property IS_ENABLED 0 [get_drc_checks {REQP-123}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design -directive Quick
    route_design -directive Quick
    route_todo
    route_design


    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
