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

set root_fp [open "root_node_${blocknb}.csv" w]

set nodes [get_nodes]

create_pblock exclude_roi
foreach roi "$::env(XRAY_EXCLUDE_ROI_TILEGRID)" {
    puts "ROI: $roi"
    resize_pblock [get_pblocks exclude_roi] -add "$roi"
}

set not_allowed_sites [get_sites -of_objects [get_pblocks exclude_roi]]
set not_allowed_nodes [get_nodes -of_objects [get_tiles -of_objects $not_allowed_sites]]

for {set j $start } { $j < $stop } { incr j } {
    set node [lindex $nodes $j]

    # If node is not allowed, skip it
    set res [lsearch $not_allowed_nodes $node]
    if { $res != -1 } {
        continue
    }

    file mkdir [file dirname "${node}"]
    set fname $node.json5
    puts $root_fp "node,,$fname"

    set fp [open "${fname}" w]
    # node properties:
    # BASE_CLOCK_REGION CLASS COST_CODE COST_CODE_NAME IS_BAD IS_COMPLETE
    # IS_GND IS_INPUT_PIN IS_OUTPUT_PIN IS_PIN IS_VCC NAME NUM_WIRES PIN_WIRE
    # SPEED_CLASS
    puts $fp "\{"
    puts $fp "\t\"node\": \"$node\","
    puts $fp "\t\"wires\": \["
    foreach wire [get_wires -of_objects $node] {
        # wire properties:
        # CLASS COST_CODE ID_IN_TILE_TYPE IS_CONNECTED IS_INPUT_PIN IS_OUTPUT_PIN
        # IS_PART_OF_BUS NAME NUM_DOWNHILL_PIPS NUM_INTERSECTS NUM_PIPS
        # NUM_TILE_PORTS NUM_UPHILL_PIPS SPEED_INDEX TILE_NAME TILE_PATTERN_OFFSET
        puts $fp "\t\t\{"
        puts $fp "\t\t\t\"wire\":\"$wire\","
        puts $fp "\t\t\},"
    }
    puts $fp "\t\]"
    puts $fp "\}"
    close $fp
}

close $root_fp
