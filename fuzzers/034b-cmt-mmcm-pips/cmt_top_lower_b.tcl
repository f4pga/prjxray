# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc print_tile_pips {tile_type filename} {
    set tile [lindex [get_tiles -filter "TYPE == $tile_type"] 0]
    puts "Dumping PIPs for tile $tile ($tile_type) to $filename."
    set fp [open $filename w]
    foreach pip [lsort [get_pips -of_objects [get_tiles $tile]]] {
        set src [get_wires -uphill -of_objects $pip]
        set dst [get_wires -downhill -of_objects $pip]
        if {[llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst]]] == 1} {
            set src_node [get_nodes -of $src]
            set dst_node [get_nodes -of $dst]

            if { [string first INT_INTERFACE [get_wires -of $src_node]] != -1 } {
                continue
            }
            if { [string first INT_INTERFACE [get_wires -of $dst_node]] != -1 } {
                continue
            }
        }
        puts $fp "$tile_type.[regsub {.*/} $dst ""].[regsub {.*/} $src ""] [get_property IS_DIRECTIONAL $pip]"
    }
    close $fp
}

proc print_tile_wires {tile_type filename} {
    set tile [lindex [get_tiles -filter "TYPE == $tile_type"] 0]
    set fp [open $filename w]
    foreach wire [lsort [get_wires -of_objects [get_tiles $tile]]] {
        puts $fp "$tile_type [regsub {.*/} $wire ""]"
    }
}

create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

print_tile_pips CMT_TOP_L_LOWER_B cmt_top_l_lower_b.txt
print_tile_pips CMT_TOP_R_LOWER_B cmt_top_r_lower_b.txt
print_tile_wires CMT_TOP_L_LOWER_B cmt_top_l_lower_b_wires.txt
print_tile_wires CMT_TOP_R_LOWER_B cmt_top_r_lower_b_wires.txt
