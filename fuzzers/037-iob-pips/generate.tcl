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
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-74}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-26}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-4}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-5}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-98}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-99}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-105}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-115}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-144}]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design -directive Quick
    write_checkpoint -force design_before_route.dcp
    make_manual_routes routes.txt
    route_design -directive Quick -preserve
    write_checkpoint -force design.dcp

    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
