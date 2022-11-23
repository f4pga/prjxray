# Copyright (C) 2017-2022  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc print_tile_pips {tile_type filename} {
    set fp [open $filename w]
    set pips [dict create]
    foreach tile [get_tiles -filter "TYPE == $tile_type"] {
        foreach pip [lsort [get_pips -of_objects  $tile]] {
            set src [get_wires -uphill -of_objects $pip]
            set dst [get_wires -downhill -of_objects $pip]

            # Skip pips with disconnected nodes
            set src_node [get_nodes -of_objects $src]

            if { $src_node == {} } {
                continue
            }

            set dst_node [get_nodes -of_objects $src]
            if { $dst_node == {} } {
                continue
            }

            set src_wire [regsub {.*/} $src ""]
            set src_match [regexp {IOI_OCLKM?_[01]} $src_wire]

            if { [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst]]] != 1 || $src_match } {
                set pip_string "$tile_type.[regsub {.*/} $dst ""].[regsub {.*/} $src ""]"
                if ![dict exists $pips $pip_string] {
                    puts $fp $pip_string
                    dict set pips $pip_string 1
                }
            }
        }
    }
    close $fp
}

create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

print_tile_pips RIOI rioi.txt
