# Copyright (C) 2017-2020  The Project X-Ray Authors
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

            set dst_node [get_nodes -of_objects $dst]
            if { $dst_node == {} } {
                continue
            }

            set dst_wire [regsub {.*/} $dst ""]
            set dst_hclk_match [regexp {HCLK_GTP_CK_IN[0-9]+} $dst_wire]

            set src_wire [regsub {.*/} $src ""]
            set src_cmt_match [regexp {HCLK_GTP_CK_MUX[0-9]+} $src_wire]

            if { $dst_hclk_match && $src_cmt_match } {
                set pip_string "GTP_COMMON.[regsub {.*/} $dst ""].[regsub {.*/} $src ""]"
                if ![dict exists $pips $pip_string] {
                    puts $fp $pip_string
                    dict set pips $pip_string 1
                }
            }
        }
    }
    close $fp
}

create_project -force -part $::env(XRAY_PART) design_ck_mux design_ck_mux
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

print_tile_pips GTP_COMMON_MID_LEFT gtp_common_mid_ck_mux.txt
