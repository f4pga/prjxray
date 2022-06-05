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

set fp [open "cmt_regions.csv" "w"]
foreach site_type {MMCME2_ADV BUFHCE BUFR BUFMRCE BUFIO ILOGICE2 OLOGICE2 IDELAYE2 IDELAYCTRL PLLE2_ADV} {
    foreach site [get_sites -filter "SITE_TYPE == $site_type"] {
        puts $fp "$site,[get_property CLOCK_REGION $site]"
    }
}
close $fp
