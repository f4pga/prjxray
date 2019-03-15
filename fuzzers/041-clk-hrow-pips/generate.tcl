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
    set fp [open "../../todo.txt" r]
    set todo_lines {}
    for {gets $fp line} {$line != ""} {gets $fp line} {
        lappend todo_lines [split $line .]
    }
    close $fp
    return $todo_lines
}

proc route_todo {} {
    puts "Checking TODO's"
    set todo_lines [load_todo]
    set srcs {}
    foreach todo $todo_lines {
        set src [lindex $todo 2]

        if [string match "*CLK_HROW_CK_IN_*" $src] {
            lappend srcs $src
        }
    }

    set srcs [lsort -unique $srcs]

    set nets [get_nets -hierarchical "*clock*"]
    set found_wires {}
    set remaining_nets {}
    foreach net $nets {
        set wires [get_wires -of_objects $net]

        foreach wire $wires {
            if [regexp "CLK_HROW_CK_IN_\[LR\]\[0-9\]+" $wire] {
                # Route already going where we want it, continue
                puts "Checking wire $wire."
                set wire [lindex [split $wire "/"] 1]
                if {[lsearch -regexp $srcs "$wire$"] != -1} {
                    puts "Found in TODO list, removing from list."
                    lappend found_wires $wire
                    # Fix route that is using target net.
                    set_property is_route_fixed 1 $net
                } else {
                    puts "Wire not in TODO list, adding to reroute list."
                    lappend remaining_nets $net
                }
                break
            }
        }
    }

    set found_wires [lsort -unique $found_wires]
    foreach wire $found_wires {
        puts "Removing $wire"
        set srcs [lsearch -regexp -all -inline -not $srcs "$wire$"]
    }

    puts "Remaining TODOs:"
    foreach src $srcs {
        puts $src
    }

    set remaining_nets [lsort -unique $remaining_nets]
    set completed_todos {}

    foreach net $remaining_nets {
        set wires [get_wires -of_objects $net]

        set clk_in_wire ""
        foreach wire $wires {
            if [regexp "CLK_HROW_CK_IN_(\[LR\])\[0-9\]+" $wire match lr] {
                set clk_in_wire $wire
                break
            }
        }

        if {$clk_in_wire == ""} {
            error "$net does not appear to be correct net for rerouting?"
        }

        puts ""
        puts "Rerouting net $net at $clk_in_wire ($lr)"

        # Find an input in the todo list that this can can drive.
        foreach src $srcs {
            if {[lsearch -exact $completed_todos $src] != -1} {
                continue
            }

            if [regexp "CLK_HROW_CK_IN_$lr\[0-9\]+" $src] {
                puts "Found target pip $src for net $net."
                set tile [get_tiles -of_objects $clk_in_wire]

                set target_wire [get_wires "$tile/$src"]
                set target_node [get_nodes -of_objects $target_wire]
                if {[llength $target_node] == 0} {
                    error "Failed to find node for $tile/$src."
                }

                set origin_node [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
                set destination_nodes [filter [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]] {NAME =~ *CLK_HROW*}]
                route_design -unroute -nets $net
                set new_route [find_routing_path -to $target_node -from $origin_node]
                puts "Origin node: $origin_node"
                puts "Target wire: $target_wire"
                puts "Target node: $target_node"
                puts "Destination nodes: $destination_nodes"

                # Only need to set route to one of the destinations.
                # Router will handle the rest.
                set_property FIXED_ROUTE [concat $new_route [lindex $destination_nodes 0]] $net

                # Remove wire, as we've found a clock to set
                lappend completed_todos $src
                break
            }
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
    route_design
    route_todo
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
