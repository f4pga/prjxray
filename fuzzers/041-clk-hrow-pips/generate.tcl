# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

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

proc load_todo {} {
    set fp [open "../../todo_all.txt" r]

    # Create map of pip destinations to remaining sources for that pip
    set todo_map [dict create]
    for {gets $fp line} {$line != ""} {gets $fp line} {
        set parts [split $line .]
        if ![string match "*CLK_HROW_CK_IN_*" [lindex $parts 2]] {
            continue
        }
        dict lappend todo_map [lindex $parts 1] [list [lindex $parts 0] [lindex $parts 2]]
    }
    close $fp
    return $todo_map
}

proc route_todo {} {
    puts "Checking TODO's"
    set todo_map [load_todo]

    set nets [get_nets]

    set todo_nets [dict create]
    set used_destinations [dict create]

    foreach net $nets {
        # Check to see if this net is one we are interested in
        set wires [get_wires -of_objects $net -filter {TILE_NAME =~ *CLK_HROW*}]

        set is_gclk_net 0
        foreach wire $wires {
            puts "Check wire $wire in $net"
            if [string match "*CLK_HROW_CK_IN_*" $wire] {
                set gclk_tile [lindex [split $wire /] 0]
                set gclk_wire [lindex [split $wire /] 1]
                set is_gclk_net 1
                break
            }
        }

        if {$is_gclk_net == 0} {
            puts "$net not going to a HCLK port, skipping."
            continue
        }

        puts "Net $net wires:"
        foreach wire [get_wires -of_objects $net] {
            puts " - $wire"
        }

        foreach wire $wires {
            set tile [lindex [split $wire /] 0]
            set wire [lindex [split $wire /] 1]
            if { $tile != $gclk_tile } {
                continue
            }

            set tile_type [get_property TILE_TYPE [get_tiles $tile]]

            if { ![dict exists $todo_map $wire] } {
                continue
            }

            set srcs [dict get $todo_map $wire]

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

                foreach src $srcs {
                    set src_tile_type [lindex $src 0]

                    if {$src_tile_type != $tile_type} {
                        continue
                    }

                    set src_wire [lindex $src 1]

                    if { $other_wire == $src_wire } {
                        set found_target 1
                        puts "Interesting net $net already going from $wire to $other_wire."
                        set_property IS_ROUTE_FIXED 1 $net
                        dict set used_destinations "$tile/$src_wire" 1
                        break
                    }
                }
            }

            if { $found_target == 1 } {
                # Net has an interesting
                continue
            }

            dict set todo_nets $net [list $tile $wire $gclk_wire]
            puts "Interesting net $net (including $wire and $gclk_wire) is being rerouted."
        }
    }

    set routed_sources [dict create]

    dict for {net tile_wire} $todo_nets {

        if { [get_property IS_ROUTE_FIXED $net] == 1 } {
            puts "Net $net is already routed, skipping."
            continue
        }

        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set gclk_wire [lindex $tile_wire 2]
        set srcs [dict get $todo_map $wire]

        puts ""
        puts "Rerouting net $net at $tile / $gclk_wire (type $tile_type)"

        set tile_type [get_property TILE_TYPE [get_tiles $tile]]
        regexp "CLK_HROW_CK_IN_(\[LR\])\[0-9\]+" $gclk_wire match lr

        set todos {}
        foreach src $srcs {
            set src_tile_type [lindex $src 0]
            if {$src_tile_type != $tile_type} {
                continue
            }

            set src_wire [lindex $src 1]

            if [regexp "CLK_HROW_CK_IN_$lr\[0-9\]+" $src_wire] {
                lappend todos $src_wire
            }
        }

        if {[llength $todos] == 0} {
            puts "No inputs for net $net."
            dict set used_destinations "$tile/$gclk_wire" 1
            continue
        }

        puts "All todos for $tile_type / $wire"
        foreach src_wire $todos {
            puts "  - $src_wire"
        }


        # Find an input in the todo list that this can can drive.
        set set_new_route 0
        foreach src_wire $todos {
            if { [dict exists $used_destinations "$tile/$src_wire"] } {
                puts "Not routing to $tile / $src_wire, in use."
                continue
            }

            puts "Attempting to route to $src_wire for net $net."

            set target_wire [get_wires "$tile/$src_wire"]
            set target_node [get_nodes -of_objects $target_wire]
            if {[llength $target_node] == 0} {
                continue
            }

            set origin_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]

            if [dict exists $routed_sources $origin_node] {
                puts "Skip net $net, already routed."
                continue
            }

            route_design -unroute -nets $net

            set old_nets [get_nets -of_objects $target_node]
            if { $old_nets != {} } {
                puts "Unrouting $old_nets"
                route_design -unroute -nets $old_nets
            }

            set old_nets [get_nets -of_objects $origin_node]
            if { $old_nets != {} } {
                puts "Unrouting $old_nets"
                route_design -unroute -nets $old_nets
            }

            set new_route [find_routing_path -to $target_node -from $origin_node]
            puts "Origin node: $origin_node"
            puts "Target wire: $target_wire"
            puts "Target node: $target_node"

            # Only need to set route to one of the destinations.
            # Router will handle the rest.
            set_property FIXED_ROUTE $new_route $net

            dict set used_destinations "$tile/$src_wire" 1
            dict set routed_sources "$origin_node" 1
            set set_new_route 1
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
    set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-123}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design
    route_design -directive Quick
    route_todo
    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
