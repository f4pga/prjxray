# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc load_todo {{dir "dst"}} {
    set fp [open "$::env(FUZDIR)/../piplist/build/gtp_common_mid_$::env(XRAY_PART)/gtp_common_mid.txt" r]

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
proc get_nets_with_todo_pip_wires {direction net_regexp wire_regexp used_destinations {verbose false} {cmt_net false}} {
    set todo_map [load_todo $direction]
    set nets [get_nets]
    set todo_nets [dict create]

    foreach net $nets {
        if {![regexp $net_regexp $net]} {
            continue
        }
        # Check to see if this net is one we are interested in*
        set wires [get_wires -of_objects $net -filter {TILE_NAME =~ "*GTP_COMMON_MID*" && (NAME =~ "*CK_IN*" || NAME =~ "*MUX*")} -quiet]

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

        if { $cmt_net } {
            dict set todo_nets $net [list $tile $wire]
            continue
        }

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
    set verbose false

    set used_destinations [dict create]

    # Re-route GTP-related nets, which are originated from the GTPE2_CHANNEL and/or IBUFDS_GTE2 primitives.
    set todo_map [load_todo "dsts"]
    set gtp_channel_nets [get_nets_with_todo_pip_wires "dsts" "gtp_channel_clock" "GTPE2_COMMON_\[TR\]XOUTCLK_MUX_\[0123\]" $used_destinations $verbose]
    set ibufds_nets [get_nets_with_todo_pip_wires "dsts" "ibufds_clock" "IBUFDS_GTPE2_\[01\]_MGTCLKOUT_MUX" $used_destinations $verbose]
    set gtp_nets [dict merge $gtp_channel_nets $ibufds_nets]
    puts "GTP nets: $gtp_nets"
    dict for {net tile_wire} $gtp_nets {
        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set dsts [dict get $todo_map $wire]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]
        set todos {}

        set old_origin_wire [get_wires -of_objects $net -filter {TILE_NAME =~ "*GTP_COMMON_MID_LEFT*" && NAME =~ "*HCLK_GTP_CK_IN*"}]
        if {$old_origin_wire == {}} {
            continue
        }

        puts "Rerouting net $net at $tile / $wire (type $tile_type)"
        puts "Previous target wire: $old_origin_wire"

        set old_origin_node [get_nodes -of_objects $old_origin_wire]
        foreach dst $dsts {
            set dst_wire [lindex $dst 1]

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

        set target_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]]
        puts "Target node: $target_node"
        route_design -unroute -nets $net

        # Find an output in the todo list that can drive.
        foreach dst_wire $todos {
            if { [dict exists $used_destinations "$tile/$dst_wire"] } {
                puts "Not routing to $tile / $dst_wire, in use."
                continue
            }

            set origin_wire [get_wires "$tile/$dst_wire"]
            set origin_node [get_nodes -of_objects $origin_wire]
            if {[llength $origin_node] == 0} {
                error "Failed to find node for $tile/$dst_wire."
            }

            set old_net [get_nets -of_objects $origin_node -quiet]
            if {$old_net != {}} {
                puts "Unrouting the old net: $old_net"
                route_design -unroute -nets $old_net
            }

            # Route the net through the desired node
            puts "Attempting to route to $dst_wire for net $net."
            set route_status [route_via $net [list $origin_node] 0]

            if {$route_status == 0} {
                puts "WARNING: route failed, continue with next todo"
                continue
            }

            puts "Target node: $target_node"
            puts "Origin wire: $origin_wire, Old origin wire: $old_origin_wire"
            puts "Origin node: $origin_node, Old origin node: $old_origin_node"

            dict set used_destinations "$origin_wire" 1

            break
        }
    }

    # Re-route CMT-related nets, which are originated from the fabric's PLL/MMCM primitives
    set todo_map [load_todo "srcs"]
    set pll_nets [get_nets_with_todo_pip_wires "srcs" "pll_clock" "HCLK_GTP_CK_IN" $used_destinations $verbose true]
    set mmcm_nets [get_nets_with_todo_pip_wires "srcs" "mmcm_clock" "HCLK_GTP_CK_IN" $used_destinations $verbose true]
    set cmt_nets [dict merge $pll_nets $mmcm_nets]
    puts "CMT nets: $cmt_nets"
    dict for {net tile_wire} $cmt_nets {
        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set dsts [dict keys $todo_map]
        set tile_type [get_property TILE_TYPE [get_tiles $tile]]
        set todos {}

        set old_origin_dst_wire [get_wires -of_objects $net -filter {TILE_NAME =~ "*GTP_COMMON_MID*"}]
        if {$old_origin_dst_wire == {}} {
            continue
        }

        # All clock nets which have a source belonging to a PLL/MMCM tile can be routed to any
        # HCLK_GTP_CK_MUX --> HCLK_GTP_CK_IN wire pair, hence we build a list of all the remaining
        # PIPs to choose from.
        puts "Rerouting net $net at $tile / $wire (type $tile_type)"
        puts "Previous target wire: $old_origin_dst_wire"

        foreach dst $dsts {
            set srcs [dict get $todo_map $dst]
            foreach src $srcs {
                # For each HCLK_GTP_CK_IN wire, get the source node (HCLK_GTP_CK_MUX) from the todo_map
                # that still needs to be documented.
                #
                # Each HCLK_GTP_CK_IN has two possible HCLK_GTP_CK_MUX sources to be paired with.
                set src_wire [lindex $src 1]

                # There are PIPs that do connect HCLK_GTP_CK_IN wires to GTP_CHANNEL- and IBUFDS-related wires.
                #
                # These kinds of PIPs are solved at a previous stage of this process, hence, the todo PIP list should
                # not contain these src/dst pairs at this stage, but only PIPs to the fabric (PLL/MMCM nets).
                set is_gtp_net 1
                if [regexp "HCLK_GTP_CK_MUX.*" $src_wire match group] {
                    set is_gtp_net 0
                }

                if {$is_gtp_net == 1} {
                    continue
                }

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

            set old_src_net [get_nets -of_objects $origin_src_node -quiet]
            if {$old_src_net != {}} {
                puts "Unrouting the old net: $old_src_net"
                route_design -unroute -nets $old_src_net
            }

            set old_dst_net [get_nets -of_objects $origin_dst_node -quiet]
            if {$old_dst_net != {}} {
                puts "Unrouting the old net: $old_dst_net"
                route_design -unroute -nets $old_dst_net
            }

            # Route the net through the desired node
            puts "Attempting to route to $src_wire and $dst_wire for net $net."
            set route_status [route_via $net [list $origin_src_node $origin_dst_node]]

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
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-29}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-38}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-47}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-123}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1575}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1619}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1684}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1712}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-50}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-78}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-81}]
    set_property IS_ENABLED 0 [get_drc_checks {PDIL-1}]


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
