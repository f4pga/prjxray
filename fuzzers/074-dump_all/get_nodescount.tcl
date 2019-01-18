create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

#set_param tcl.collectionResultDisplayLimit 0
set_param messaging.disableStorage 1

set nbnodes_fp [open nb_nodes.txt w]

set nodes [get_nodes]
puts $nbnodes_fp [llength $nodes]

close $nbnodes_fp
