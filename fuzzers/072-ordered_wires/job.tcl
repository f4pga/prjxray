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

set pips [get_pips]

set dwnhill_fp [open "wires/downhill_wires_${blocknb}.txt" w]
set uphill_fp [open "wires/uphill_wires_${blocknb}.txt" w]

for { set i $start } { $i < $stop } { incr i } {
    set pip [lindex $pips $i]
    foreach downhill_node [get_nodes -downhill -of_object $pip] {
        set ordered_downhill_wires [get_wires -from $pip -of_object $downhill_node]
        puts $dwnhill_fp "$pip $downhill_node $ordered_downhill_wires"
    }
    foreach uphill_node [get_nodes -uphill -of_object $pip] {
        set ordered_uphill_wires [get_wires -to $pip -of_object $uphill_node]
        puts $uphill_fp "$pip $uphill_node $ordered_uphill_wires"
    }

}

close $dwnhill_fp
close $uphill_fp
