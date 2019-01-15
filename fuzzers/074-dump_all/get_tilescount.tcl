create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

#set_param tcl.collectionResultDisplayLimit 0
set_param messaging.disableStorage 1

set nbtiles_fp [open nb_tiles.txt w]

set tiles [get_tiles]
puts $nbtiles_fp [llength $tiles]

close $nbtiles_fp
