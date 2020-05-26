# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open $::env(XRAY_PART)_package_pins.csv w]
puts $fp "pin,bank,site,tile,pin_function"
foreach pin [get_package_pins] {
    set site [get_sites -quiet -of_object $pin]
    if { $site == "" } {
        continue
    }

    set tile [get_tiles -of_object $site]
    set pin_bank [get_property BANK [get_package_pins $pin]]
    set pin_function [get_property PIN_FUNC [get_package_pins $pin]]

    puts $fp "$pin,$pin_bank,$site,$tile,$pin_function"
}
