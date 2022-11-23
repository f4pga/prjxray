# Copyright (C) 2017-2022  The Project X-Ray Authors
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
proc get_nets_with_todo_pip_wires {direction net_regexp wire_regexp used_destinations {verbose false}} {
    set todo_map [load_todo $direction]
    puts $todo_map
    set nets [get_nets]
    set todo_nets [dict create]

    foreach net $nets {
        if {![regexp $net_regexp $net]} {
            continue
        }
        # Check to see if this net is one we are interested in*
        set wires [get_wires -of_objects $net -filter {TILE_NAME =~ "*HCLK_IOI*" } -quiet]

        set wire_found 0
        foreach wire $wires {
            if [regexp $wire_regexp $wire] {
                set wire_found 1
                break
            }
        }

        if {$wire_found == 0} {
            if {$verbose} {
                puts "$net not going to a HCLK port, skipping."
            }
            continue
        }

        set tile [lindex [split $wire /] 0]
        set wire [lindex [split $wire /] 1]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]


        if { ![dict exists $todo_map $wire] } {
            continue
        }

        set candidates [dict get $todo_map $wire]

        # This net is interesting, see if it is already going somewhere we
        # want.
        set found_target 0
        foreach other_wire $wires {
            if { $found_target == 1 } {
                break
            }

            set other_wire [lindex [split $other_wire /] 1]

            if { $wire == $other_wire } {
                continue
            }

            foreach candidate $candidates {
                set candidate_tile_type [lindex $candidate 0]

                if {$candidate_tile_type != $tile_type} {
                    continue
                }

                set candidate_wire [lindex $candidate 1]

                if { $other_wire == $candidate } {
                    set found_target 1
                    if {$verbose} {
                        puts "Interesting net $net already going from $wire to $other_wire."
                    }
                    set_property IS_ROUTE_FIXED 1 $net
                    dict set used_destinations "$tile/$candidate_wire" 1
                    break
                }
            }
        }

        if { $found_target == 1 } {
            # Net already has an interesting feature - don't reroute.
            continue
        }

        dict set todo_nets $net [list $tile $wire]
        if {$verbose} {
            puts "Interesting net $net (including $wire) is being rerouted."
        }
    }
    return $todo_nets
}

proc route_todo {} {
    set used_destinations [dict create]
    set todo_map [load_todo "dsts"]
    set serdes_nets [get_nets_with_todo_pip_wires "dsts" "serdes_clk_ILOGIC" "HCLK_IOI_CK_IGCLK" $used_destinations]
    puts "Serdes nets: $serdes_nets"
    dict for {net tile_wire} $serdes_nets {
        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set dsts [dict get $todo_map $wire]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]
        set todos {}

        set old_target_wire [get_wires -of_objects $net -filter {TILE_NAME =~ "*HCLK_IOI*" && NAME =~ "*HCLK_IOI_LEAF_GCLK_*"}]
        if {$old_target_wire == {}} {
            continue
        }
        if {[dict exists $used_destinations $old_target_wire]} {
            puts "Not routing to $old_target_wire, in use."
            continue
        }
        puts "Rerouting net $net at $tile / $wire (type $tile_type)"
        puts "Previous target wire: $old_target_wire"
        set old_target_node [get_nodes -of_objects $old_target_wire]
        if [regexp "HCLK_IOI_LEAF_GCLK_\(\(TOP\)|\(BOT\)\).*" $old_target_wire match group] {
            set old_target_side $group
        }
        foreach dst $dsts {
            set dst_tile_type [lindex $dst 0]
            if {$dst_tile_type != $tile_type} {
                continue
            }

            set dst_wire [lindex $dst 1]

            set is_gclk_net 0
            if [regexp "HCLK_IOI_LEAF_GCLK_\(\(TOP\)|\(BOT\)\).*" $dst_wire match group] {
                set is_gclk_net 1
                set dst_side $group
            }

            if {$is_gclk_net == 0 || $dst_side != $old_target_side} {
                continue
            }

            lappend todos $dst_wire
        }

        set todos_length [llength $todos]
        if {$todos_length == 0} {
            continue
        }

        puts "All todos for $tile_type / $wire"
        foreach dst_wire $todos {
            puts "  - $dst_wire"
        }

        set todos [shuffle_list $todos]

        set origin_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
        puts "Origin node: $origin_node"
        route_design -unroute -nets $net

        # Find an input in the todo list that this can can drive.
        foreach dst_wire $todos {
            if { [dict exists $used_destinations "$tile/$dst_wire"] } {
                puts "Not routing to $tile / $dst_wire, in use."
                continue
            }

            set target_wire [get_wires "$tile/$dst_wire"]
            set target_node [get_nodes -of_objects $target_wire]
            if {[llength $target_node] == 0} {
                error "Failed to find node for $tile/$dst_wire."
            }

            set old_net [get_nets -of_objects $target_node -quiet]
            if {$old_net == {}} {
                continue
            }
            puts "Unrouting the old net: $old_net"
            route_design -unroute -nets $old_net
            set old_origin_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $old_net]]

            # Route the net through the desired node
            puts "Attempting to route to $target_node for net $net."
            route_via $net [list $target_node]

            puts "Attempting to route to $old_target_node for net $old_net."
            # Route the old net through the old target node
            route_via $old_net [list $old_target_node ]

            puts "Origin node: $origin_node, Old origin node: $old_origin_node"
            puts "Target wire: $target_wire, Old target wire: $old_target_wire"
            puts "Target node: $target_node, Old target node: $old_target_node"

            dict set used_destinations "$target_wire" 1
            dict set used_destinations "$old_target_wire" 1

            break
        }
    }

    set todo_map [load_todo "srcs"]
    set before_div_nets [get_nets_with_todo_pip_wires "srcs" "I_BUFR" "HCLK_IOI_RCLK_BEFORE_DIV" $used_destinations]
    puts "Before div nets: $before_div_nets"
    dict for {net tile_wire} $before_div_nets {
        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set srcs [dict get $todo_map $wire]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]
        set todos {}

        set old_origin_wire [get_wires -of_objects $net -filter {TILE_NAME =~ "*HCLK_IOI*" && NAME =~ "*HCLK_IOI_RCLK_IMUX*"}]
        if {$old_origin_wire == {}} {
            continue
        }

        puts "Rerouting net $net at $tile / $wire (type $tile_type)"
        puts "Previous target wire: $old_origin_wire"

        set old_origin_node [get_nodes -of_objects $old_origin_wire]
        if [regexp "HCLK_IOI_RCLK_IMUX.*" $old_origin_wire match group] {
            set old_target_side $group
        }
        foreach src $srcs {
            set src_tile_type [lindex $src 0]
            if {$src_tile_type != $tile_type} {
                continue
            }

            set src_wire [lindex $src 1]

            set is_gclk_net 0
            if [regexp "HCLK_IOI_RCLK_IMUX.*" $src_wire match group] {
                set is_gclk_net 1
            }

            if {$is_gclk_net == 0} {
                continue
            }

            lappend todos $src_wire
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
        foreach src_wire $todos {
            if { [dict exists $used_destinations "$tile/$src_wire"] } {
                puts "Not routing to $tile / $src_wire, in use."
                continue
            }

            set origin_wire [get_wires "$tile/$src_wire"]
            set origin_node [get_nodes -of_objects $origin_wire]
            if {[llength $origin_node] == 0} {
                error "Failed to find node for $tile/$src_wire."
            }

            set old_net [get_nets -of_objects $origin_node -quiet]
            if {$old_net != {}} {
                puts "Unrouting the old net: $old_net"
                route_design -unroute -nets $old_net
            }

            # Route the net through the desired node
            puts "Attempting to route to $src_wire for net $net."
            route_via $net [list $origin_node]

            puts "Target node: $target_node"
            puts "Origin wire: $origin_wire, Old origin wire: $old_origin_wire"
            puts "Origin node: $origin_node, Old origin node: $old_origin_node"

            dict set used_destinations "$origin_wire" 1

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
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-29}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-38}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-123}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1575}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1684}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1712}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-50}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-78}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-81}]


    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design
    route_design
    route_todo
    route_design


    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
