create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

#set_param tcl.collectionResultDisplayLimit 0
set_param messaging.disableStorage 1

set nbpips_fp [open nb_pips.txt w]

set pips [get_pips]
puts $nbpips_fp [llength $pips]
