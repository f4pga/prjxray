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
    set fp [open "../todo.txt" r]

    # Create map of pip source to remaining destinations for that pip
    set todo_map [dict create]
    for {gets $fp line} {$line != ""} {gets $fp line} {
        set parts [split $line .]
        dict lappend todo_map [lindex $parts 1] [list [lindex $parts 0] [lindex $parts 2]]
    }
    close $fp
    return $todo_map
}

proc route_todo {} {
    puts "Checking TODO's"
    set todo_map [load_todo]

    puts $todo_map

    set nets [get_nets]

    set todo_nets [dict create]
    set used_sources [dict create]

    foreach net $nets {
        # Check to see if this net is one we are interested in
        set wires [get_wires -of_objects $net -filter {TILE_NAME =~ *IOI3*}]
        set is_gclk_net 0
        foreach wire $wires {
            if [regexp "IOI_\[IO\]LOGIC\[01\]_CLKB?" $wire] {
                set is_gclk_net 1
                break
            }
            if [regexp "IOI_OCLK_\[01\]" $wire] {
                set is_gclk_net 1
                break
            }
            if [regexp "IOI_\[IO\]LOGIC\[01\]_CLKDIV" $wire] {
                set is_gclk_net 1
                break
            }
        }

        if {$is_gclk_net == 0} {
            puts "$net not going to a IOI3 port, skipping."
            continue
        }

        foreach wire $wires {
            set tile [lindex [split $wire /] 0]
            set wire [lindex [split $wire /] 1]
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

                    if { $other_wire == $src } {
                        set found_target 1
                        puts "Interesting net $net already going from $wire to $other_wire."
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
        set srcs [dict get $todo_map $wire]
        set site [lindex [get_sites -of_objects [get_tiles $tile]] 0]
        set region [get_clock_regions -of_objects [get_sites $site]]

        puts "Rerouting net $net at $tile / $wire (type $tile_type)"

        set tile_type [get_property TILE_TYPE [get_tiles $tile]]

        set todos {}
        foreach src $srcs {
            set src_tile_type [lindex $src 0]
            if {$src_tile_type != $tile_type} {
                continue
            }

            set src_wire [lindex $src 1]

            set is_gclk_net 0
            if [regexp "IOI_LEAF_GCLK\[0-9\]+" $src_wire] {
                set is_gclk_net 1
            }

            if {$is_gclk_net == 0} {
                continue
            }

            lappend todos $src_wire
        }

        puts "All todos for $tile_type / $wire"
        foreach src_wire $todos {
            puts "  - $src_wire"
        }

        route_design -unroute -nets $net

        # Find an input in the todo list that this can can drive.
        foreach src_wire $todos {
            puts "Attempting to route to $src_wire for net $net."
            set target_wire [get_wires "$tile/$src_wire"]
            set target_node [get_nodes -of_objects $target_wire]

            if {[llength $target_node] == 0} {
                error "Failed to find node for $tile/$src_wire."
            }

            if { [regexp ".*TOP.*" $target_node match group] } {
                set loc TOP
            } elseif { [regexp ".*BOT.*" $target_node match group] } {
                set loc BOT
            }

            if { [dict exists $used_sources "$region/$loc/$src_wire"] } {
                puts "Not routing to $tile / $src_wire, in use."
                continue
            }


            set old_nets [get_nets -of_objects $target_node]

            if { $old_nets != {} } {
                set old_nets_property [get_property IS_ROUTE_FIXED [get_nets -of_objects $target_node]]
                if { $old_nets_property == 0 } {
                    route_design -unroute -nets $old_nets
                }
            }

            set origin_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
            set new_route [find_routing_path -to $target_node -from $origin_node]
            puts "Origin node: $origin_node"
            puts "Target wire: $target_wire"
            puts "Target node: $target_node"

            # Only need to set route to one of the destinations.
            # Router will handle the rest.
            set_property FIXED_ROUTE $new_route $net

            dict set used_sources "$region/$loc/$src_wire" 1
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
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-74}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-26}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-4}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-5}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-98}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-99}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-115}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-144}]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design
    write_checkpoint -force design_before_route.dcp
    route_design
    write_checkpoint -force design_before.dcp

    #route_todo
    route_design
    write_checkpoint -force design_after.dcp

    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
