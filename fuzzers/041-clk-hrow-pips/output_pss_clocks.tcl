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

set fp [open "pss_clocks.csv" "w"]
puts $fp "pin,wire,tile,clock_regions"

# List all PSS_HCLK wires
set pss_clk_wires [get_wires *PSS_HCLK* -of_objects [get_tiles PSS*]]
foreach wire $pss_clk_wires {

    # Get PIPs that mention the wire inside a CLK_HROW tile. Take the first one.
    set pips [get_pips CLK_HROW_* -of_objects [get_nodes -of_objects $wire]]
    set pip [lindex $pips 0]

    # Get the CLK_HROW tile.
    set tile [get_tiles -of_objects $pip]

    # Get the name of the input wire of the CLK_HROW tile. This is different
    # than the name of the PSS clock wire. Do it by parsing the PIP name
    set cmt_wire [lindex [split [lindex [split $pip "-"] 0] "."] 1]

    # Get clock regions of the tile. CLK_HROW tiles span two regions.
    set regions [dict create]
    foreach site [get_sites -of_objects $tile] {
        set region [get_property CLOCK_REGION $site]
        dict incr regions $region
    }

    set regions [dict keys $regions]

    # Get uphill PIP, parse its name to get the PS7 wire name. This will be
    # actually the wire of the PSS tile but the important part of the name
    # is the same.
    set pip [get_pips -uphill -of_objects $wire]
    set pin [lindex [split [lindex [split $pip "."] 1] "-"] 0]

    puts $fp "$pin,$cmt_wire,$tile,$regions"
}

close $fp
