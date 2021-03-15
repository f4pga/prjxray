# Copyright (C) 2017-2021  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

proc dump_pins {file_name site_prefix} {
    set fp [open $file_name w]

    puts $fp "name,is_input,is_output"
    set site [lindex [get_sites $site_prefix*] 0]

    set pins [get_site_pins -of_objects $site]
    foreach pin $pins {
        set connected_pip [get_pips -of_objects [get_nodes -of_objects $pin]]

        if { $connected_pip == "" } {
            continue
        }

        set pin_name [lindex [split $pin "/"] 1]
        set is_input [get_property IS_INPUT $pin]
        set is_output [get_property IS_OUTPUT $pin]

        puts $fp "$pin_name,$is_input,$is_output"
    }
    close $fp
}

create_project -force -name design -part $::env(XRAY_PART)
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

dump_pins $::env(FILE_NAME) PCIE
