# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
create_project -force -name design -part $::env(XRAY_PART)
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open ps7_pins.csv w]
puts $fp "name,is_input,is_output,is_bidir"

set pins [get_bel_pins -of_objects [get_bels -of_objects [get_sites PS7* -of_objects [get_tiles PSS*]]]]
foreach pin $pins {

    set pin_name [lindex [split $pin "/"] 2]
    set is_input [get_property IS_INPUT $pin]
    set is_output [get_property IS_OUTPUT $pin]
    set is_bidir [get_property IS_BIDIR $pin]

    puts $fp "$pin_name,$is_input,$is_output,$is_bidir"
}

close $fp
