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
set fp [open "iobanks.txt" "w"]
foreach iobank [get_iobanks] {
    foreach site [get_sites -of $iobank] {
        puts $fp "$site,$iobank"
    }
}
close $fp

set fp [open "cmt_regions.csv" "w"]
foreach site_type { IOB33M IOB33S IDELAYCTRL} {
    foreach site [get_sites -filter "SITE_TYPE == $site_type"] {
        set tile [get_tiles -of $site]
        # exclude IDELAYCTRL from high speed banks
        if {![string match "*_IOI_*" $tile]} {
            puts $fp "$site,$tile,[get_property CLOCK_REGION $site]"
        }
    }
}
close $fp

set fp [open "pudc_sites.csv" "w"]
puts $fp "tile,site"
foreach tile [get_tiles *IOB33*] {
    foreach site [get_sites -of_objects $tile] {
        set site_type [get_property SITE_TYPE $site]

        set pin [get_package_pins -of_objects $site]
        set pin_func [get_property PIN_FUNC $pin]

        if {[string first "PUDC_B" $pin_func] != -1} {
            puts $fp "$tile,$site,$site_type"
        }
    }
}
close $fp
