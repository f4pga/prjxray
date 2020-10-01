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

proc write_used_wires {filename} {
    puts "FUZ([pwd]): Writing $filename."

    set fp [open $filename w]
    set nets [get_nets -hierarchical]
    set nnets [llength $nets]
    set neti 0
    foreach net $nets {
        foreach node [get_nodes -of $net] {
            foreach wire [get_wires -of $node] {
                puts $fp "$wire"
            }
        }
    }
    close $fp
}

proc load_routes {filename} {
    puts "MANROUTE: Loading routes from $filename"

    set fp [open $filename r]
    foreach line [split [read $fp] "\n"] {
        if {$line eq ""} {
            continue
        }

        puts "MANROUTE: Line: $line"

        # Parse the line
        set fields [split $line " "]
        set tile_name [lindex $fields 0]
        set site_name [lindex $fields 1]
        set pin_name  [lindex $fields 2]
        set route_dir [lindex $fields 3]
        set wires [lrange $fields 4 end]

        # Get net
        set tile [get_tiles $tile_name]
        set site [get_sites -of_objects $tile $site_name]
        set pin [get_site_pins -of_objects $site "*/$pin_name"]
        set net [get_nets -quiet -of_objects $pin]

        if {$net eq "" } {
            puts "MANROUTE: No net for pin $pin_name found! Skipping..."
            continue
        }

        # Fixed part read from file
        set route_list {}
        foreach wire $wires {
            lappend route_list [get_nodes -of_objects [get_wires -of_objects $tile "*/$wire"]]
        }

        # Complete the route
        if {$route_dir eq "up"} {
            set node_to [lindex $route_list 0]
            set node_from [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]

            set rpart [find_routing_path -from $node_from -to $node_to]
            if {$rpart eq ""} {
                puts "MANROUTE: No possible route continuation for net $net"
                continue
            }

            set route_list [concat [lrange $rpart 0 end-1] $route_list]
        }

        if {$route_dir eq "down"} {
            set node_from [lindex $route_list e]
            set node_to [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]]

            set rpart [find_routing_path -from $node_from -to $node_to]
            if {$rpart eq ""} {
                puts "MANROUTE: No possible route continuation for net $net"
                continue
            }
            set route_list [concat $route_list [lrange $rpart 1 end]]
        }

        # Set the fixed route
        puts "MANROUTE: Net: $net, Route: $route_list. routing..."
        regsub -all {{}} $route_list "" route
        set_property FIXED_ROUTE $route $net

        # Route the single net. Needed to detect conflicts when evaluating
        # other ones
        route_design -quiet -directive Quick -nets $net

        # Check for conflicts.
        set status [get_property ROUTE_STATUS $net]
        if {$status ne "ROUTED"} {
            # Ripup and discard the fixed route.
            set_property FIXED_ROUTE "" $net
            route_design -unroute -nets $net
            puts "MANROUTE: Net $net status $status, ripping up..."
        } else {
            set_property IS_ROUTE_FIXED 1 $net
            puts "MANROUTE: Successful manual route for $net"
        }
    }

    close $fp
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    # Disable MMCM frequency etc sanity checks
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-29}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-30}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-50}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-53}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-126}]
    # PLL
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-43}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-78}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-81}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-38}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]

    place_design

    load_routes routes.txt
    write_checkpoint -force design_pre_route.dcp

    route_design -directive Quick -preserve

    if {[llength [get_nets -filter {ROUTE_STATUS!="ROUTED"}]] ne 0} {
        set nets [get_nets -filter {IS_ROUTE_FIXED==1}]
        puts "MANROUTE: Got unrouted nets: $nets"
        puts "MANROUTE: Ripping up and starting again with no fixed routes"

        route_design -unroute
        set_property FIXED_ROUTE "" $nets
        set_property IS_ROUTE_FIXED 0 $nets

        route_design -directive Quick
    }

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design_pips.txt
    write_used_wires design_wires.txt
}

run
