# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(FUZDIR)/util.tcl"

proc write_tiles_txt {} {
    # Get all tiles, ie not just the selected LUTs
    set tiles [get_tiles]
    set not_allowed_sites [get_sites -of_objects [get_pblocks exclude_roi]]

    # Write tiles.txt with site metadata
    set fp [open "tiles.txt" w]
    set fp_pin [open "pin_func.txt" w]
    foreach tile $tiles {
        set type [get_property TYPE $tile]
        set grid_x [get_property GRID_POINT_X $tile]
        set grid_y [get_property GRID_POINT_Y $tile]
        set sites [get_sites -quiet -of_objects $tile]

        # There are some sites which are not allowed to be placed.
        # This check excludes tiles in the EXCLUDE_ROI pblock
        # be added to tilegrid.json
        set skip_tile 0
        foreach site $sites {
            set res [lsearch $not_allowed_sites $site]
            if { $res != -1 } {
                set skip_tile 1
                break
            }
        }

        set typed_sites {}

        set clock_region "NA"

        if [llength $sites] {
            set site_types [get_property SITE_TYPE $sites]
            foreach t $site_types s $sites {
                lappend typed_sites $t $s
                lappend typed_sites [get_property PROHIBIT $s]

                set package_pin [get_package_pins -of $s -quiet]
                if [llength $package_pin] {
                    puts $fp_pin "$s [get_property PIN_FUNC $package_pin]"
                }
                set clock_region [get_property CLOCK_REGION $s]
            }
        }
        if {[llength $clock_region] == 0} {
            set clock_region "NA"
        }


        puts $fp "$type $tile $grid_x $grid_y $skip_tile $clock_region $typed_sites"
    }
    close $fp_pin
    close $fp
}

proc run {} {
    # Generate grid of entire part
    make_project_roi XRAY_ROI_TILEGRID XRAY_EXCLUDE_ROI_TILEGRID

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_tiles_txt
}

run
