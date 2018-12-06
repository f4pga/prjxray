create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set downhill_fp [open downhill_wires.txt w]
set uphill_fp [open uphill_wires.txt w]
#set_param tcl.collectionResultDisplayLimit 0
foreach pip [get_pips] {
    foreach downhill_node [get_nodes -downhill -of_object $pip] {
        set ordered_downhill_wires [get_wires -from $pip -of_object $downhill_node]
        puts $downhill_fp "$pip $downhill_node $ordered_downhill_wires"
    }
    foreach uphill_node [get_nodes -uphill -of_object $pip] {
        set ordered_uphill_wires [get_wires -to $pip -of_object $uphill_node]
        puts $uphill_fp "$pip $uphill_node $ordered_uphill_wires"
    }
}
close $downhill_fp
close $uphill_fp
