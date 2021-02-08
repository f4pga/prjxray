# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc route_delay {} {
    set nets [get_nets]

    foreach net $nets {
        set wire [get_wires -of_objects $net -filter { TILE_NAME =~ "*PCIE_INT_INTERFACE*" && NAME =~ "*IMUX*OUT*" }]

        if { $wire == "" } {
            continue
        }

        if { rand() < 0.30 } {
            continue
        }

        set parts [split $wire "/"]
        set tile_name [lindex $parts 0]
        set wire_name [lindex $parts 1]

        set delay_wire_name [string map {OUT DELAY} $wire_name]
        set delay_node [get_nodes $tile_name/$delay_wire_name]

        if { $delay_node == "" } {
            exit 1
        }

        route_design -unroute -nets $net
        puts "Attempting to route net $net through $delay_node."
        route_via $net [list $delay_node]
    }
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design -directive Quick
    route_design -directive Quick

    route_delay

    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
