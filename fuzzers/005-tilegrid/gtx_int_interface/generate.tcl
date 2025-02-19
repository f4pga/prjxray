# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc parse_csv {} {
    set fp [open "params.csv"]
    set file_data [read $fp]
    close $fp

    set file_data [split $file_data "\n"]

    set params_map [dict create]

    set is_first_line true
    foreach line $file_data {
        if { $is_first_line } {
            set is_first_line false
            continue
        }

        # Skip empty lines
        if { $line == "" } {
            continue
        }

        set parts [split $line ","]

        dict lappend params_map [lindex $parts 2] [lindex $parts 1]
    }

    return $params_map
}


proc route_through_delay {} {
    set params_map [parse_csv]

    dict for { key value } $params_map {
        if { $value == 0 } {
            continue
        }

        set net_name "QPLLLOCKEN_$key"
        set net [get_nets $net_name]

        set wire [get_wires -of_objects $net -filter {TILE_NAME =~ "*GTX_INT_INTERFACE*" && NAME =~ "*IMUX_OUT24*"}]
        set wire_parts [split $wire "/"]

        set gtx_int_tile [lindex $wire_parts 0]
        set node [get_nodes -of_object [get_tiles $gtx_int_tile] -filter { NAME =~ "*DELAY24" }]

        route_design -unroute -nets $net
        puts "Attempting to route net $net through $node."
        route_via $net [list $node]
    }
}


proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    # Disable MMCM frequency etc sanity checks
    set_property IS_ENABLED 0 [get_drc_checks {REQP-47}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-48}]

    place_design
    route_design

    route_through_delay

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
