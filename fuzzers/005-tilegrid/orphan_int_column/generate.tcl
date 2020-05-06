# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt

    set fp [open top.txt]
    set int_tiles [split [read $fp] "\n"]
    close $fp

    set fp [open design.txt]
    set pips [split [read $fp] "\n"]
    close $fp

    set found_int_tiles {}
    foreach pip $pips {
        set parts [split $pip " "]
        set tile_idx [lsearch -exact $int_tiles [lindex $parts 0]]

        if {$tile_idx == -1} {
            continue
        }

        set tile [lindex $int_tiles $tile_idx]
        set pip_of_interest "$tile/INT_L.EL1END1->>EE2BEG1"
        if { $pip_of_interest == [lindex $parts 1] } {
            lappend found_int_tiles $tile
        }
    }

    set fp [open params.csv "w"]
    puts $fp "tile,val"
    foreach tile $int_tiles {
        if {$tile == ""} {
            continue
        }

        set pip_active [lsearch -exact $found_int_tiles $tile]
        if {$pip_active != -1} {
            puts $fp "$tile,1"
        } else {
            puts $fp "$tile,0"
        }
    }
    close $fp
}

run
