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

    # Create map of pip source to remaining destinations for that pip
    set todo_map [dict create]
    for {gets $fp line} {$line != ""} {gets $fp line} {
        set parts [split $line .]
        dict lappend todo_map [lindex $parts 2] [list [lindex $parts 0] [lindex $parts 1]]
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
        set wires [get_wires -of_objects $net -filter {TILE_NAME =~ *HCLK_CMT*}]

        set is_gclk_net 0
        foreach wire $wires {
            if [regexp "HCLK_CMT_MUX_CLK_\[0-9\]+" $wire] {
                set is_gclk_net 1
                break
            }
            if [regexp "HCLK_CMT_CK_IN\[0-9\]+" $wire] {
                set is_gclk_net 1
                break
            }
        }

        if {$is_gclk_net == 0} {
            puts "$net not going to a HCLK port, skipping."
            continue
        }

        foreach wire $wires {
            set tile [lindex [split $wire /] 0]
            set wire [lindex [split $wire /] 1]
            set tile_type [get_property TILE_TYPE [get_tiles $tile]]

            if { ![dict exists $todo_map $wire] } {
                continue
            }

            set dsts [dict get $todo_map $wire]

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

                foreach dst $dsts {
                    set dst_tile_type [lindex $dst 0]

                    if {$dst_tile_type != $tile_type} {
                        continue
                    }

                    set dst_wire [lindex $dst 1]

                    if { $other_wire == $dst } {
                        set found_target 1
                        puts "Interesting net $net already going from $wire to $other_wire."
                        set_property IS_ROUTE_FIXED 1 $net
                        dict set used_destinations "$tile/$dst_wire" 1
                        break
                    }
                }
            }

            if { $found_target == 1 } {
                # Net has an interesting
                continue
            }

            dict set todo_nets $net [list $tile $wire]
            puts "Interesting net $net (including $wire) is being rerouted."
        }
    }

    dict for {net tile_wire} $todo_nets {
        set tile [lindex $tile_wire 0]
        set wire [lindex $tile_wire 1]
        set dsts [dict get $todo_map $wire]

        puts "Rerouting net $net at $tile / $wire (type $tile_type)"

        set tile_type [get_property TILE_TYPE [get_tiles $tile]]

        set todos {}
        foreach dst $dsts {
            set dst_tile_type [lindex $dst 0]
            if {$dst_tile_type != $tile_type} {
                continue
            }

            set dst_wire [lindex $dst 1]

            set is_gclk_net 0
            if [regexp "HCLK_CMT_MUX_CLK_\[0-9\]+" $dst_wire] {
                set is_gclk_net 1
            }
            if [regexp "HCLK_CMT_CK_IN\[0-9\]+" $dst_wire] {
                set is_gclk_net 1
            }

            if {$is_gclk_net == 0} {
                continue
            }

            lappend todos $dst_wire
        }

        puts "All todos for $tile_type / $wire"
        foreach dst_wire $todos {
            puts "  - $dst_wire"
        }

        route_design -unroute -nets $net

        # Find an input in the todo list that this can can drive.
        foreach dst_wire $todos {
            if { [dict exists $used_destinations "$tile/$dst_wire"] } {
                puts "Not routing to $tile / $dst_wire, in use."
                continue
            }

            puts "Attempting to route to $dst_wire for net $net."

            set target_wire [get_wires "$tile/$dst_wire"]
            set target_node [get_nodes -of_objects $target_wire]
            if {[llength $target_node] == 0} {
                error "Failed to find node for $tile/$dst_wire."
            }

            set old_nets [get_nets -of_objects $target_node]

            if { $old_nets != {} } {
                route_design -unroute -nets $old_nets
            }

            set origin_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
            set new_route [find_routing_path -to $target_node -from $origin_node]
            puts "Origin node: $origin_node"
            puts "Target wire: $target_wire"
            puts "Target node: $target_node"

            # Only need to set route to one of the destinations.
            # Router will handle the rest.
            set_property FIXED_ROUTE $new_route $net

            dict set used_destinations "$tile/$dst_wire" 1
            break
        }
    }
}

proc make_manual_routes {filename} {
    puts "MANROUTE: Loading routes from $filename"

    set fp [open $filename r]
    foreach line [split [read $fp] "\n"] {
        if {$line eq ""} {
            continue
        }

        puts "MANROUTE: Line: $line"

        # Parse the line
        set fields [split $line " "]
        set net_name [lindex $fields 0]
        set wire_name [lindex $fields 1]

        # Check if that net exist
        if {[get_nets $net_name] eq ""} {
            puts "MANROUTE: net $net_name does not exist"
            continue
        }

        set net [get_nets $net_name]

        # Rip it up
        set_property -quiet FIXED_ROUTE "" $net
        set_property IS_ROUTE_FIXED 0 $net
        route_design -unroute -nets $net

        # Make the route
        set nodes [get_nodes -of_objects [get_wires $wire_name]]
        set status [route_via $net_name [list $nodes] 0]

        # Failure, skip manual routing of this net
        if { $status != 1 } {
            puts "MANROUTE: Manual routing failed!"
            set_property -quiet FIXED_ROUTE "" $net
            set_property IS_ROUTE_FIXED 0 $net
            continue
        }

        puts "MANROUTE: Success!"
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

    place_design -directive Quick
    route_design -directive Quick
    route_todo
    make_manual_routes routes.txt
    route_design -directive Quick -preserve

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
