# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
set blocknb [lindex $argv 0]
set start [expr int([lindex $argv 1])]
set stop [expr int([lindex $argv 2])]

create_project -force -part $::env(XRAY_PART) $blocknb $blocknb
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

#set_param tcl.collectionResultDisplayLimit 0
set_param messaging.disableStorage 1

set root_fp [open "root_${blocknb}.csv" w]
#puts $root_fp "filetype,subtype,filename"

set tiles [get_tiles]

create_pblock exclude_roi
foreach roi "$::env(XRAY_EXCLUDE_ROI_TILEGRID)" {
    puts "ROI: $roi"
    resize_pblock [get_pblocks exclude_roi] -add "$roi"
}

set not_allowed_sites [get_sites -of_objects [get_pblocks exclude_roi]]
set not_allowed_tiles [get_tiles -of_objects $not_allowed_sites]

for {set j $start } { $j < $stop } { incr j } {

    set tile [lindex $tiles $j]

    # If tile is not allowed, skip it
    set res [lsearch $not_allowed_tiles $tile]
    if { $res != -1 } {
        set ignored 1
    } else {
        set ignored 0
    }

    set fname tile_$tile.json5
    set tile_type [get_property TYPE $tile]
    puts $root_fp "tile,$tile_type,$fname"

    set fp [open "${fname}" w]
    puts $fp "\{"
    puts $fp "\t\"tile\": \"$tile\","
    puts $fp "\t\"ignored\": \"$ignored\","
    # tile properties:
    # CLASS COLUMN DEVICE_ID FIRST_SITE_ID GRID_POINT_X GRID_POINT_Y INDEX
    # INT_TILE_X INT_TILE_Y IS_CENTER_TILE IS_DCM_TILE IS_GT_CLOCK_SITE_TILE
    # IS_GT_SITE_TILE NAME NUM_ARCS NUM_SITES ROW SLR_REGION_ID
    # TILE_PATTERN_IDX TILE_TYPE TILE_TYPE_INDEX TILE_X TILE_Y TYPE
    puts $fp "\t\"type\": \"$tile_type\","
    puts $fp "\t\"x\": [get_property GRID_POINT_X $tile],"
    puts $fp "\t\"y\": [get_property GRID_POINT_Y $tile],"
    puts $fp "\t\"sites\": \["
    foreach site [get_sites -of_objects $tile] {
        # site properties:
        # ALTERNATE_SITE_TYPES CLASS CLOCK_REGION IS_BONDED IS_CLOCK_BUFFER
        # IS_CLOCK_PAD IS_GLOBAL_CLOCK_BUFFER IS_GLOBAL_CLOCK_PAD IS_PAD
        # IS_REGIONAL_CLOCK_BUFFER IS_REGIONAL_CLOCK_PAD IS_RESERVED IS_TEST
        # IS_USED MANUAL_ROUTING NAME NUM_ARCS NUM_BELS NUM_INPUTS NUM_OUTPUTS
        # NUM_PINS PRIMITIVE_COUNT PROHIBIT PROHIBIT_FROM_PERSIST RPM_X RPM_Y
        # SITE_PIPS SITE_TYPE

        puts $fp "\t\t\{"
        puts $fp "\t\t\t\"site\":\"$site\","
        puts $fp "\t\t\t\"type\":\"[get_property SITE_TYPE $site]\","
        puts $fp "\t\t\t\"site_pins\": \["
        foreach site_pin [get_site_pins -of_objects $site] {
            # site_pin properties:
            # CLASS DIRECTION INDEX INDEX_IN_BUS INDEX_IN_SITE INDEX_IN_TILE IS_BAD
            # IS_INPUT IS_OUTPUT IS_PART_OF_BUS IS_TEST IS_USED NAME SITE_ID
            # SPEED_INDEX
            puts $fp "\t\t\t\{"
            puts $fp "\t\t\t\t\"site_pin\":\"$site_pin\","

            set site_pin_speed_model_index [get_property SPEED_INDEX $site_pin]
            puts $fp "\t\t\t\t\"speed_model_index\":\"$site_pin_speed_model_index\","

            set dir [get_property DIRECTION $site_pin]
            puts $fp "\t\t\t\t\"direction\":\"$dir\","
            set site_pin_node [get_nodes -of_objects $site_pin]
            if {[llength $site_pin_node] == 0} {
                puts $fp "\t\t\t\t\"node\":null,"
            } else {
                puts $fp "\t\t\t\t\"node\":\"$site_pin_node\","
            }
            puts $fp "\t\t\t\},"
        }
        puts $fp "\t\t\t\],"
        puts $fp "\t\t\t\"site_pips\": \["
        foreach site_pip [get_site_pips -of_objects $site] {
            puts $fp "\t\t\t\{"
            # site_pips properties:
            # CLASS FROM_PIN IS_FIXED IS_USED NAME SITE TO_PIN
            puts $fp "\t\t\t\t\"site_pip\":\"$site_pip\","
            puts $fp "\t\t\t\t\"to_pin\":\"[get_property TO_PIN $site_pip]\","
            puts $fp "\t\t\t\t\"from_pin\":\"[get_property FROM_PIN $site_pip]\","
            puts $fp "\t\t\t\},"
        }
        puts $fp "\t\t\t\],"

        puts $fp "\t\t\t\"package_pins\": \["
        foreach package_pin [get_package_pins -of_objects $site] {
            puts $fp "\t\t\t\t\{"
            puts $fp "\t\t\t\t\t\"package_pin\":\"$package_pin\","
            puts $fp "\t\t\t\t\},"
        }
        puts $fp "\t\t\t\],"

        puts $fp "\t\t\},"
    }
    puts $fp "\t\],"
    puts $fp "\t\"pips\": \["
    foreach pip [get_pips -of_objects $tile] {
        # pip properties:
        # CAN_INVERT CLASS IS_BUFFERED_2_0 IS_BUFFERED_2_1 IS_DIRECTIONAL
        # IS_EXCLUDED_PIP IS_FIXED_INVERSION IS_INVERTED IS_PSEUDO IS_SITE_PIP
        # IS_TEST_PIP NAME SPEED_INDEX TILE
        puts $fp "\t\t\{"
        puts $fp "\t\t\t\"pip\":\"$pip\","

        set pip_speed_model_index [get_property SPEED_INDEX $pip]
        puts $fp "\t\t\t\"speed_model_index\":\"$pip_speed_model_index\","
        puts $fp "\t\t\t\"src_wire\":\"[get_wires -uphill -of_objects $pip]\","
        puts $fp "\t\t\t\"dst_wire\":\"[get_wires -downhill -of_objects $pip]\","
        puts $fp "\t\t\t\"is_pseudo\":\"[get_property IS_PSEUDO $pip]\","
        puts $fp "\t\t\t\"is_directional\":\"[get_property IS_DIRECTIONAL $pip]\","
        puts $fp "\t\t\t\"can_invert\":\"[get_property CAN_INVERT $pip]\","
        puts $fp "\t\t\},"
    }
    puts $fp "\t\],"

    puts $fp "\t\"wires\": \["
    foreach wire [get_wires -of_objects $tile] {
        # wire properties:
        # CLASS COST_CODE ID_IN_TILE_TYPE IS_CONNECTED IS_INPUT_PIN IS_OUTPUT_PIN
        # IS_PART_OF_BUS NAME NUM_DOWNHILL_PIPS NUM_INTERSECTS NUM_PIPS
        # NUM_TILE_PORTS NUM_UPHILL_PIPS SPEED_INDEX TILE_NAME TILE_PATTERN_OFFSET
        puts $fp "\t\t\{"
        puts $fp "\t\t\t\"wire\":\"$wire\","

        set wire_speed_model_index [get_property SPEED_INDEX $wire]
        puts $fp "\t\t\t\t\"speed_model_index\":\"$wire_speed_model_index\","
        puts $fp "\t\t\},"
    }
    puts $fp "\t\],"
    puts $fp "\}"
    close $fp
}

close $root_fp
